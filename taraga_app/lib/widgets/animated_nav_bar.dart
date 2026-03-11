import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Animated bottom navigation bar icon
class AnimatedNavIcon extends StatefulWidget {
  final Widget icon;
  final bool isSelected;
  final Color selectedColor;
  final Color unselectedColor;

  const AnimatedNavIcon({
    super.key,
    required this.icon,
    required this.isSelected,
    this.selectedColor = Colors.blueAccent,
    this.unselectedColor = Colors.white54,
  });

  @override
  State<AnimatedNavIcon> createState() => _AnimatedNavIconState();
}

class _AnimatedNavIconState extends State<AnimatedNavIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _bounceAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );

    _scaleAnimation = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );

    _bounceAnimation = Tween<double>(begin: 0.0, end: -3.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    if (widget.isSelected) _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedNavIcon oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isSelected != oldWidget.isSelected) {
      if (widget.isSelected) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, _bounceAnimation.value),
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: widget.icon,
          ),
        );
      },
    );
  }
}

/// 클린 플로팅 네비게이션 바 — 토스 스타일
class AnimatedBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;
  final List<BottomNavItem> items;

  const AnimatedBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(20, 0, 20, 16),
      child: Container(
        height: 68,
        decoration: BoxDecoration(
          color: AppColors.bgWhite,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF191F28).withOpacity(0.08),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
            BoxShadow(
              color: const Color(0xFF191F28).withOpacity(0.04),
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: List.generate(items.length, (index) {
            final item = items[index];
            final isSelected = currentIndex == index;

            return Expanded(
              child: GestureDetector(
                onTap: () => onTap(index),
                behavior: HitTestBehavior.opaque,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    AnimatedNavIcon(
                      icon: item.iconBuilder(
                        isSelected ? item.selectedColor : item.unselectedColor,
                        isSelected ? 24 : 22,
                      ),
                      isSelected: isSelected,
                      selectedColor: item.selectedColor,
                      unselectedColor: item.unselectedColor,
                    ),
                    const SizedBox(height: 4),
                    AnimatedDefaultTextStyle(
                      duration: const Duration(milliseconds: 250),
                      style: TextStyle(
                        fontSize: isSelected ? 11 : 10,
                        fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                        color: isSelected
                            ? item.selectedColor
                            : item.unselectedColor,
                      ),
                      child: Text(item.label),
                    ),
                    const SizedBox(height: 4),
                    // 깔끔한 닷 인디케이터
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 300),
                      curve: Curves.easeOutCubic,
                      width: isSelected ? 5 : 0,
                      height: isSelected ? 5 : 0,
                      decoration: BoxDecoration(
                        color: item.selectedColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                  ],
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}

class BottomNavItem {
  final Widget Function(Color color, double size) iconBuilder;
  final String label;
  final Color selectedColor;
  final Color unselectedColor;

  BottomNavItem({
    required this.iconBuilder,
    required this.label,
    this.selectedColor = AppColors.primary,
    this.unselectedColor = AppColors.textLight,
  });
}

import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'home_screen.dart';
import 'insight_screen.dart';
import 'calendar_screen.dart';
import 'mypage_screen.dart';
import '../widgets/animated_nav_bar.dart';
import '../widgets/custom_icons.dart';
import '../theme/app_theme.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const HomeScreen(),
    const InsightScreen(),
    const CalendarScreen(),
    const MyPageScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBody: true,
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: AnimatedBottomNavBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: [
          BottomNavItem(
            iconBuilder: (color, size) => TaragaIcons.home(color: color, size: size),
            label: '홈',
            selectedColor: AppColors.primary,
          ),
          BottomNavItem(
            iconBuilder: (color, size) => TaragaIcons.insight(color: color, size: size),
            label: '인사이트',
            selectedColor: AppColors.accentOrange,
          ),
          BottomNavItem(
            iconBuilder: (color, size) => TaragaIcons.calendar(color: color, size: size),
            label: '캘린더',
            selectedColor: AppColors.accentGreen,
          ),
          BottomNavItem(
            iconBuilder: (color, size) => TaragaIcons.profile(color: color, size: size),
            label: '내 정보',
            selectedColor: AppColors.accentPurple,
          ),
        ],
      ),
    );
  }
}

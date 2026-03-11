import 'package:flutter/material.dart';
import 'dart:ui';

/// Taraga 밝은 금융앱 디자인 시스템
/// Inspired by Toss(토스), Robinhood — 깨끗하고 신뢰감 있는 라이트 테마
class AppColors {
  // ─── Backgrounds (밝고 깨끗한) ───
  static const Color bgPrimary = Color(0xFFF7F8FC);     // 메인 배경 — 아이보리 화이트
  static const Color bgWhite = Color(0xFFFFFFFF);        // 카드/서피스
  static const Color bgSecondary = Color(0xFFF0F2F8);    // 세컨더리 배경
  static const Color bgBlueLight = Color(0xFFEEF2FF);    // 블루 틴트 배경
  static const Color bgCard = Color(0xFFFFFFFF);

  // ─── Primary Brand Color (신뢰감 있는 블루) ───
  static const Color primary = Color(0xFF3182F6);        // 토스 블루
  static const Color primaryLight = Color(0xFFD6E4FF);   // 라이트 블루
  static const Color primaryDark = Color(0xFF1B64DA);

  // ─── Semantic Colors ───
  static const Color success = Color(0xFF00C073);        // 상승/성공 — 토스 그린
  static const Color danger = Color(0xFFFF5247);         // 하락/에러
  static const Color warning = Color(0xFFFF9F43);        // 경고/주의
  static const Color info = Color(0xFF5B7FFF);           // 정보

  // ─── Market Colors (Korean Standard) ───
  static const Color marketUp = Color(0xFFFF5247);       // 상승 (빨강)
  static const Color marketDown = Color(0xFF3182F6);     // 하락 (파랑)

  // ─── Accent Colors (밝고 생동감) ───
  static const Color accentPurple = Color(0xFF7C5CFC);
  static const Color accentCyan = Color(0xFF36B5E6);
  static const Color accentPink = Color(0xFFFF6B8A);
  static const Color accentGreen = Color(0xFF00C073);
  static const Color accentOrange = Color(0xFFFF9F43);
  static const Color accentBlue = Color(0xFF3182F6);

  // ─── Text Colors ───
  static const Color textPrimary = Color(0xFF191F28);    // 거의 블랙
  static const Color textSecondary = Color(0xFF4E5968);  // 다크 그레이
  static const Color textMuted = Color(0xFF8B95A1);      // 미드 그레이
  static const Color textLight = Color(0xFFB0B8C1);      // 라이트 그레이
  static const Color textOnPrimary = Color(0xFFFFFFFF);  // 프라이머리 위 흰색

  // ─── Border & Divider ───
  static const Color border = Color(0xFFE5E8EB);
  static const Color divider = Color(0xFFF2F4F6);

  // ─── Gradients (부드러운 그라데이션) ───
  static const LinearGradient blueGradient = LinearGradient(
    colors: [Color(0xFF3182F6), Color(0xFF5B7FFF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient purpleGradient = LinearGradient(
    colors: [Color(0xFF7C5CFC), Color(0xFFB18CFF)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient greenGradient = LinearGradient(
    colors: [Color(0xFF00C073), Color(0xFF36B5E6)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient warmGradient = LinearGradient(
    colors: [Color(0xFFFF9F43), Color(0xFFFF6B8A)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient bgGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      Color(0xFFF7F8FC),
      Color(0xFFFFFFFF),
    ],
  );
}

class AppDecorations {
  /// 클린 카드 (그림자 기반)
  static BoxDecoration cleanCard({
    double borderRadius = 16,
    Color? color,
  }) {
    return BoxDecoration(
      color: color ?? AppColors.bgWhite,
      borderRadius: BorderRadius.circular(borderRadius),
      boxShadow: [
        BoxShadow(
          color: const Color(0xFF191F28).withOpacity(0.04),
          blurRadius: 12,
          offset: const Offset(0, 4),
        ),
        BoxShadow(
          color: const Color(0xFF191F28).withOpacity(0.02),
          blurRadius: 2,
          offset: const Offset(0, 1),
        ),
      ],
    );
  }

  /// 액센트 보더 카드
  static BoxDecoration accentCard({
    Color accentColor = AppColors.primary,
    double borderRadius = 16,
  }) {
    return BoxDecoration(
      color: AppColors.bgWhite,
      borderRadius: BorderRadius.circular(borderRadius),
      border: Border.all(color: accentColor.withOpacity(0.15), width: 1.5),
      boxShadow: [
        BoxShadow(
          color: accentColor.withOpacity(0.06),
          blurRadius: 16,
          offset: const Offset(0, 4),
        ),
        BoxShadow(
          color: const Color(0xFF191F28).withOpacity(0.03),
          blurRadius: 4,
          offset: const Offset(0, 1),
        ),
      ],
    );
  }

  /// 네온 카드 (하위 호환용 alias)
  static BoxDecoration neonCard({
    Color glowColor = AppColors.primary,
    double glowIntensity = 0.3,
    double borderRadius = 16,
  }) {
    return accentCard(accentColor: glowColor, borderRadius: borderRadius);
  }
}

/// 깨끗한 카드 위젯 (기존 NeonGlassCard 대체 + Hover Effect)
class NeonGlassCard extends StatefulWidget {
  final Widget child;
  final Color glowColor;
  final double glowIntensity;
  final double borderRadius;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double blur;
  final VoidCallback? onTap;

  const NeonGlassCard({
    super.key,
    required this.child,
    this.glowColor = AppColors.primary,
    this.glowIntensity = 0.2,
    this.borderRadius = 16,
    this.padding,
    this.margin,
    this.blur = 0,
    this.onTap,
  });

  @override
  State<NeonGlassCard> createState() => _NeonGlassCardState();
}

class _NeonGlassCardState extends State<NeonGlassCard> {
  bool _isHovered = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: MouseRegion(
        onEnter: (_) => setState(() => _isHovered = true),
        onExit: (_) => setState(() => _isHovered = false),
        cursor: widget.onTap != null ? SystemMouseCursors.click : SystemMouseCursors.basic,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
          margin: widget.margin,
          transform: Matrix4.identity()..scale(_isHovered ? 1.02 : 1.0),
          decoration: BoxDecoration(
            color: AppColors.bgWhite,
            borderRadius: BorderRadius.circular(widget.borderRadius),
            border: Border.all(
              color: widget.glowColor.withOpacity(_isHovered ? 0.3 : 0.12),
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: widget.glowColor.withOpacity(_isHovered ? 0.15 : 0.06),
                blurRadius: _isHovered ? 24 : 16,
                offset: const Offset(0, 4),
              ),
              BoxShadow(
                color: const Color(0xFF191F28).withOpacity(0.03),
                blurRadius: 4,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            child: Container(
              padding: widget.padding,
              child: widget.child,
            ),
          ),
        ),
      ),
    );
  }
}

/// 그라데이션 텍스트
class GradientText extends StatelessWidget {
  final String text;
  final TextStyle style;
  final Gradient gradient;

  const GradientText({
    super.key,
    required this.text,
    required this.style,
    this.gradient = AppColors.blueGradient,
  });

  @override
  Widget build(BuildContext context) {
    return ShaderMask(
      blendMode: BlendMode.srcIn,
      shaderCallback: (bounds) => gradient.createShader(
        Rect.fromLTWH(0, 0, bounds.width, bounds.height),
      ),
      child: Text(text, style: style),
    );
  }
}

/// 컬러 닷 인디케이터
class NeonDot extends StatelessWidget {
  final Color color;
  final double size;

  const NeonDot({
    super.key,
    required this.color,
    this.size = 6,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Custom animated loading indicator
/// Can be replaced with Rive animation later
class AnimatedLoadingIndicator extends StatefulWidget {
  final double size;
  final Color color;

  const AnimatedLoadingIndicator({
    super.key,
    this.size = 60,
    this.color = Colors.blue,
  });

  @override
  State<AnimatedLoadingIndicator> createState() => _AnimatedLoadingIndicatorState();
}

class _AnimatedLoadingIndicatorState extends State<AnimatedLoadingIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            painter: _LoadingPainter(
              progress: _controller.value,
              color: widget.color,
            ),
          );
        },
      ),
    );
  }
}

class _LoadingPainter extends CustomPainter {
  final double progress;
  final Color color;

  _LoadingPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    // Draw rotating arc
    final sweepAngle = 2 * math.pi * 0.75;
    final startAngle = 2 * math.pi * progress;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(_LoadingPainter oldDelegate) => true;
}

/// Success animation with checkmark
class AnimatedSuccessIndicator extends StatefulWidget {
  final double size;
  final Color color;

  const AnimatedSuccessIndicator({
    super.key,
    this.size = 60,
    this.color = Colors.green,
  });

  @override
  State<AnimatedSuccessIndicator> createState() => _AnimatedSuccessIndicatorState();
}

class _AnimatedSuccessIndicatorState extends State<AnimatedSuccessIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _checkAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _scaleAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 0.5, curve: Curves.elasticOut),
    );

    _checkAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.3, 1.0, curve: Curves.easeOut),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: CustomPaint(
              painter: _SuccessPainter(
                progress: _checkAnimation.value,
                color: widget.color,
              ),
            ),
          );
        },
      ),
    );
  }
}

class _SuccessPainter extends CustomPainter {
  final double progress;
  final Color color;

  _SuccessPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    // Draw circle
    canvas.drawCircle(center, radius, paint);

    // Draw checkmark
    if (progress > 0) {
      final path = Path();
      final checkStart = Offset(size.width * 0.25, size.height * 0.5);
      final checkMiddle = Offset(size.width * 0.45, size.height * 0.7);
      final checkEnd = Offset(size.width * 0.75, size.height * 0.3);

      path.moveTo(checkStart.dx, checkStart.dy);
      
      if (progress < 0.5) {
        final currentX = checkStart.dx + (checkMiddle.dx - checkStart.dx) * (progress * 2);
        final currentY = checkStart.dy + (checkMiddle.dy - checkStart.dy) * (progress * 2);
        path.lineTo(currentX, currentY);
      } else {
        path.lineTo(checkMiddle.dx, checkMiddle.dy);
        final currentX = checkMiddle.dx + (checkEnd.dx - checkMiddle.dx) * ((progress - 0.5) * 2);
        final currentY = checkMiddle.dy + (checkEnd.dy - checkMiddle.dy) * ((progress - 0.5) * 2);
        path.lineTo(currentX, currentY);
      }

      canvas.drawPath(path, paint);
    }
  }

  @override
  bool shouldRepaint(_SuccessPainter oldDelegate) => true;
}

/// Error animation with X mark
class AnimatedErrorIndicator extends StatefulWidget {
  final double size;
  final Color color;

  const AnimatedErrorIndicator({
    super.key,
    this.size = 60,
    this.color = Colors.red,
  });

  @override
  State<AnimatedErrorIndicator> createState() => _AnimatedErrorIndicatorState();
}

class _AnimatedErrorIndicatorState extends State<AnimatedErrorIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _shakeAnimation;
  late Animation<double> _xAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 600),
    );

    _shakeAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.3, curve: Curves.elasticOut),
      ),
    );

    _xAnimation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.2, 1.0, curve: Curves.easeOut),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          final shake = math.sin(_shakeAnimation.value * math.pi * 4) * 5;
          return Transform.translate(
            offset: Offset(shake, 0),
            child: CustomPaint(
              painter: _ErrorPainter(
                progress: _xAnimation.value,
                color: widget.color,
              ),
            ),
          );
        },
      ),
    );
  }
}

class _ErrorPainter extends CustomPainter {
  final double progress;
  final Color color;

  _ErrorPainter({required this.progress, required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;

    // Draw circle
    canvas.drawCircle(center, radius, paint);

    // Draw X mark
    if (progress > 0) {
      final padding = size.width * 0.3;
      
      // First line (top-left to bottom-right)
      if (progress < 0.5) {
        final currentProgress = progress * 2;
        final endX = padding + (size.width - padding * 2) * currentProgress;
        final endY = padding + (size.height - padding * 2) * currentProgress;
        canvas.drawLine(
          Offset(padding, padding),
          Offset(endX, endY),
          paint,
        );
      } else {
        canvas.drawLine(
          Offset(padding, padding),
          Offset(size.width - padding, size.height - padding),
          paint,
        );
        
        // Second line (top-right to bottom-left)
        final currentProgress = (progress - 0.5) * 2;
        final endX = size.width - padding - (size.width - padding * 2) * currentProgress;
        final endY = padding + (size.height - padding * 2) * currentProgress;
        canvas.drawLine(
          Offset(size.width - padding, padding),
          Offset(endX, endY),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(_ErrorPainter oldDelegate) => true;
}

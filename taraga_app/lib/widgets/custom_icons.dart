import 'package:flutter/material.dart';
import 'dart:math' as math;

/// Modern custom icons for Taraga app
class TaragaIcons {
  // Custom painted icons for bottom navigation
  
  /// Home icon - Modern house with bridge element
  static Widget home({required Color color, required double size}) {
    return CustomPaint(
      size: Size(size, size),
      painter: _HomeIconPainter(color: color),
    );
  }

  /// Insight icon - Lightbulb with spark
  static Widget insight({required Color color, required double size}) {
    return CustomPaint(
      size: Size(size, size),
      painter: _InsightIconPainter(color: color),
    );
  }

  /// Calendar icon - Modern minimal calendar
  static Widget calendar({required Color color, required double size}) {
    return CustomPaint(
      size: Size(size, size),
      painter: _CalendarIconPainter(color: color),
    );
  }

  /// Profile icon - Modern user avatar
  static Widget profile({required Color color, required double size}) {
    return CustomPaint(
      size: Size(size, size),
      painter: _ProfileIconPainter(color: color),
    );
  }
}

// Home Icon Painter
class _HomeIconPainter extends CustomPainter {
  final Color color;

  _HomeIconPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path();
    
    // House roof
    path.moveTo(size.width * 0.5, size.height * 0.2);
    path.lineTo(size.width * 0.8, size.height * 0.45);
    path.lineTo(size.width * 0.8, size.height * 0.8);
    path.lineTo(size.width * 0.2, size.height * 0.8);
    path.lineTo(size.width * 0.2, size.height * 0.45);
    path.close();

    canvas.drawPath(path, paint);

    // Door
    final doorRect = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        size.width * 0.4,
        size.height * 0.55,
        size.width * 0.2,
        size.height * 0.25,
      ),
      const Radius.circular(2),
    );
    canvas.drawRRect(doorRect, paint);
  }

  @override
  bool shouldRepaint(_HomeIconPainter oldDelegate) => oldDelegate.color != color;
}

// Insight Icon Painter (Lightbulb)
class _InsightIconPainter extends CustomPainter {
  final Color color;

  _InsightIconPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    // Bulb
    final bulbPath = Path();
    bulbPath.moveTo(size.width * 0.5, size.height * 0.2);
    bulbPath.quadraticBezierTo(
      size.width * 0.7, size.height * 0.3,
      size.width * 0.7, size.height * 0.5,
    );
    bulbPath.lineTo(size.width * 0.6, size.height * 0.65);
    bulbPath.lineTo(size.width * 0.4, size.height * 0.65);
    bulbPath.lineTo(size.width * 0.3, size.height * 0.5);
    bulbPath.quadraticBezierTo(
      size.width * 0.3, size.height * 0.3,
      size.width * 0.5, size.height * 0.2,
    );

    canvas.drawPath(bulbPath, paint);

    // Base
    canvas.drawLine(
      Offset(size.width * 0.4, size.height * 0.7),
      Offset(size.width * 0.6, size.height * 0.7),
      paint,
    );
    canvas.drawLine(
      Offset(size.width * 0.42, size.height * 0.75),
      Offset(size.width * 0.58, size.height * 0.75),
      paint,
    );

    // Spark
    paint.style = PaintingStyle.fill;
    final sparkPath = Path();
    sparkPath.moveTo(size.width * 0.75, size.height * 0.25);
    sparkPath.lineTo(size.width * 0.78, size.height * 0.28);
    sparkPath.lineTo(size.width * 0.75, size.height * 0.31);
    sparkPath.lineTo(size.width * 0.72, size.height * 0.28);
    sparkPath.close();
    canvas.drawPath(sparkPath, paint);
  }

  @override
  bool shouldRepaint(_InsightIconPainter oldDelegate) => oldDelegate.color != color;
}

// Calendar Icon Painter
class _CalendarIconPainter extends CustomPainter {
  final Color color;

  _CalendarIconPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    // Calendar body
    final rect = RRect.fromRectAndRadius(
      Rect.fromLTWH(
        size.width * 0.2,
        size.height * 0.25,
        size.width * 0.6,
        size.height * 0.55,
      ),
      const Radius.circular(4),
    );
    canvas.drawRRect(rect, paint);

    // Top line
    canvas.drawLine(
      Offset(size.width * 0.2, size.height * 0.4),
      Offset(size.width * 0.8, size.height * 0.4),
      paint,
    );

    // Rings
    canvas.drawLine(
      Offset(size.width * 0.35, size.height * 0.2),
      Offset(size.width * 0.35, size.height * 0.3),
      paint,
    );
    canvas.drawLine(
      Offset(size.width * 0.65, size.height * 0.2),
      Offset(size.width * 0.65, size.height * 0.3),
      paint,
    );

    // Dots (dates)
    paint.style = PaintingStyle.fill;
    final dotSize = size.width * 0.06;
    for (var i = 0; i < 2; i++) {
      for (var j = 0; j < 3; j++) {
        canvas.drawCircle(
          Offset(
            size.width * (0.3 + j * 0.2),
            size.height * (0.5 + i * 0.15),
          ),
          dotSize,
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(_CalendarIconPainter oldDelegate) => oldDelegate.color != color;
}

// Profile Icon Painter
class _ProfileIconPainter extends CustomPainter {
  final Color color;

  _ProfileIconPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round;

    // Head
    canvas.drawCircle(
      Offset(size.width * 0.5, size.height * 0.35),
      size.width * 0.15,
      paint,
    );

    // Body (shoulders)
    final bodyPath = Path();
    bodyPath.moveTo(size.width * 0.25, size.height * 0.8);
    bodyPath.quadraticBezierTo(
      size.width * 0.3, size.height * 0.55,
      size.width * 0.5, size.height * 0.55,
    );
    bodyPath.quadraticBezierTo(
      size.width * 0.7, size.height * 0.55,
      size.width * 0.75, size.height * 0.8,
    );

    canvas.drawPath(bodyPath, paint);
  }

  @override
  bool shouldRepaint(_ProfileIconPainter oldDelegate) => oldDelegate.color != color;
}

/// Taraga Logo - Modern bridge symbol
class TaragaLogo extends StatelessWidget {
  final double size;
  final Color color;

  const TaragaLogo({
    super.key,
    this.size = 32,
    this.color = Colors.blueAccent,
  });

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(size, size),
      painter: _TaragaLogoPainter(color: color),
    );
  }
}

class _TaragaLogoPainter extends CustomPainter {
  final Color color;

  _TaragaLogoPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    // Bridge arc
    final path = Path();
    path.moveTo(size.width * 0.1, size.height * 0.7);
    path.quadraticBezierTo(
      size.width * 0.5, size.height * 0.2,
      size.width * 0.9, size.height * 0.7,
    );

    canvas.drawPath(path, paint);

    // Support pillars
    canvas.drawLine(
      Offset(size.width * 0.3, size.height * 0.5),
      Offset(size.width * 0.3, size.height * 0.7),
      paint,
    );
    canvas.drawLine(
      Offset(size.width * 0.7, size.height * 0.5),
      Offset(size.width * 0.7, size.height * 0.7),
      paint,
    );

    // Gradient effect (using multiple strokes)
    final gradientPaint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 6.0
      ..strokeCap = StrokeCap.round;

    canvas.drawPath(path, gradientPaint);
  }

  @override
  bool shouldRepaint(_TaragaLogoPainter oldDelegate) => oldDelegate.color != color;
}

import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const TaragaApp());
}

class TaragaApp extends StatelessWidget {
  const TaragaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Taraga - 따라가',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue,
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        fontFamily: 'Noto Sans KR',
        scaffoldBackgroundColor: const Color(0xFF0A0E27),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF1A1F3A),
          elevation: 0,
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

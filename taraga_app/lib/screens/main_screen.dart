import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import 'home_screen.dart';
import 'insight_screen.dart';
import 'calendar_screen.dart';
import 'mypage_screen.dart';

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
      body: IndexedStack(
        index: _selectedIndex,
        children: _screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: Color(0xFF1E1E2C), width: 1.0),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: _onItemTapped,
          backgroundColor: const Color(0xFF0A0E27), // Match Scaffold background
          selectedItemColor: Colors.blueAccent,
          unselectedItemColor: Colors.white54,
          type: BottomNavigationBarType.fixed,
          showUnselectedLabels: true,
          selectedFontSize: 12,
          unselectedFontSize: 12,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.home),
              label: '홈',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.news),
              label: '인사이트',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.calendar),
              label: '캘린더',
            ),
            BottomNavigationBarItem(
              icon: Icon(CupertinoIcons.person),
              label: '내 정보',
            ),
          ],
        ),
      ),
    );
  }
}

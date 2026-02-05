import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final ApiService _apiService = ApiService();
  
  CalendarFormat _calendarFormat = CalendarFormat.month;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  
  // Map of date string to list of events
  Map<String, List<dynamic>> _events = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _selectedDay = _focusedDay;
    _loadEvents();
  }

  Future<void> _loadEvents() async {
    setState(() => _isLoading = true);
    try {
      final eventsList = await _apiService.getCalendarEvents(_focusedDay.year, _focusedDay.month);
      
      final Map<String, List<dynamic>> newEvents = {};
      for (var event in eventsList) {
        final date = event['date']; // YYYY-MM-DD
        if (newEvents[date] == null) {
          newEvents[date] = [];
        }
        newEvents[date]!.add(event);
      }
      
      setState(() {
        _events = newEvents;
        _isLoading = false;
      });
    } catch (e) {
      print("Error loading calendar events: $e");
      setState(() => _isLoading = false);
    }
  }

  List<dynamic> _getEventsForDay(DateTime day) {
    final dateStr = DateFormat('yyyy-MM-dd').format(day);
    return _events[dateStr] ?? [];
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E2C), // Dark theme background
      appBar: AppBar(
        title: const Text('주요 경제 일정', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadEvents,
          )
        ],
      ),
      body: Column(
        children: [
          _buildCalendar(),
          const SizedBox(height: 16),
          Expanded(child: _buildEventList()),
        ],
      ),
    );
  }

  Widget _buildCalendar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF2C2C3E), // Card background
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 10,
            offset: Offset(0, 4),
          )
        ],
      ),
      child: TableCalendar(
        firstDay: DateTime.utc(2023, 1, 1),
        lastDay: DateTime.utc(2030, 12, 31),
        focusedDay: _focusedDay,
        calendarFormat: _calendarFormat,
        selectedDayPredicate: (day) {
          return isSameDay(_selectedDay, day);
        },
        onDaySelected: (selectedDay, focusedDay) {
          if (!isSameDay(_selectedDay, selectedDay)) {
            setState(() {
              _selectedDay = selectedDay;
              _focusedDay = focusedDay;
            });
          }
        },
        onFormatChanged: (format) {
          if (_calendarFormat != format) {
            setState(() {
              _calendarFormat = format;
            });
          }
        },
        onPageChanged: (focusedDay) {
          _focusedDay = focusedDay;
          _loadEvents(); // Reload for new month
        },
        eventLoader: _getEventsForDay,
        
        // Styles
        headerStyle: const HeaderStyle(
          formatButtonVisible: false,
          titleCentered: true,
          titleTextStyle: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
          leftChevronIcon: Icon(Icons.chevron_left, color: Colors.white70),
          rightChevronIcon: Icon(Icons.chevron_right, color: Colors.white70),
        ),
        daysOfWeekStyle: const DaysOfWeekStyle(
          weekdayStyle: TextStyle(color: Colors.white70),
          weekendStyle: TextStyle(color: Colors.redAccent),
        ),
        calendarStyle: CalendarStyle(
          defaultTextStyle: const TextStyle(color: Colors.white),
          weekendTextStyle: const TextStyle(color: Colors.redAccent),
          outsideTextStyle: TextStyle(color: Colors.white.withOpacity(0.3)),
          selectedDecoration: const BoxDecoration(
            color: Colors.blueAccent,
            shape: BoxShape.circle,
          ),
          todayDecoration: BoxDecoration(
            color: Colors.blueAccent.withOpacity(0.3),
            shape: BoxShape.circle,
          ),
          markerDecoration: const BoxDecoration(
            color: Colors.orangeAccent,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }

  Widget _buildEventList() {
    final selectedEvents = _selectedDay != null 
        ? _getEventsForDay(_selectedDay!) 
        : [];
      
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (selectedEvents.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.event_busy, size: 64, color: Colors.white.withOpacity(0.2)),
            const SizedBox(height: 16),
            Text(
              "이 날짜엔 주요 일정이 없습니다.",
              style: TextStyle(color: Colors.white.withOpacity(0.5)),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      itemCount: selectedEvents.length,
      itemBuilder: (context, index) {
        final event = selectedEvents[index];
        return _buildEventCard(event);
      },
    );
  }
  
  Widget _buildEventCard(dynamic event) {
    Color scoreColor = Colors.greenAccent;
    final int score = event['impact_score'] ?? 0;
    
    if (score >= 90) scoreColor = Colors.redAccent;
    else if (score >= 70) scoreColor = Colors.orangeAccent;
    
    final bool isEconomic = event['type'] == 'ECONOMIC';
    final IconData icon = isEconomic 
        ? Icons.account_balance 
        : (event['type'] == 'EARNINGS' ? Icons.monetization_on : Icons.calendar_today);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF2C2C3E),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: scoreColor.withOpacity(0.3), width: 1),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: scoreColor.withOpacity(0.2),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: scoreColor, size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      event['country'] == 'US' ? '🇺🇸 미국' : '🇰🇷 한국',
                      style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: scoreColor,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        "시장 영향력 $score",
                        style: const TextStyle(color: Colors.black, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  event['title'] ?? 'Unknown Event',
                  style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 6),
                Text(
                  event['description'] ?? '',
                  style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

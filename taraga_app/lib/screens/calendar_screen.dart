import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});
  @override State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final ApiService _apiService = ApiService();
  CalendarFormat _calendarFormat = CalendarFormat.month;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  Map<DateTime, List<dynamic>> _events = {};
  bool _isLoading = false;

  @override
  void initState() { super.initState(); _loadEvents(); }

  Future<void> _loadEvents() async {
    setState(() => _isLoading = true);
    try {
      final events = await _apiService.getCalendarEvents(_focusedDay.year, _focusedDay.month);
      Map<DateTime, List<dynamic>> eventMap = {};
      for (var event in events) {
        final date = DateTime.parse(event['date']);
        final key = DateTime(date.year, date.month, date.day);
        eventMap[key] = [...(eventMap[key] ?? []), event];
      }
      setState(() { _events = eventMap; _isLoading = false; });
    } catch (e) { setState(() => _isLoading = false); }
  }

  List<dynamic> _getEventsForDay(DateTime day) => _events[DateTime(day.year, day.month, day.day)] ?? [];

  @override
  Widget build(BuildContext context) {
    final selectedEvents = _selectedDay != null ? _getEventsForDay(_selectedDay!) : <dynamic>[];

    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: MediaQuery.of(context).padding.top + 16),
            Row(children: [
              const Text('📅', style: TextStyle(fontSize: 24)),
              const SizedBox(width: 8),
              Text('경제 캘린더', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.textPrimary, letterSpacing: -0.5)),
            ]),
            const SizedBox(height: 8),
            Text('주요 경제 지표 발표 일정을 확인하세요.', style: TextStyle(color: AppColors.textMuted, fontSize: 14)),
            const SizedBox(height: 20),

            // Calendar
            NeonGlassCard(
              glowColor: AppColors.primary,
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
              child: TableCalendar(
                firstDay: DateTime.utc(2020, 1, 1),
                lastDay: DateTime.utc(2030, 12, 31),
                focusedDay: _focusedDay,
                calendarFormat: _calendarFormat,
                selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                eventLoader: _getEventsForDay,
                onDaySelected: (selectedDay, focusedDay) {
                  setState(() { _selectedDay = selectedDay; _focusedDay = focusedDay; });
                },
                onFormatChanged: (fmt) => setState(() => _calendarFormat = fmt),
                onPageChanged: (focusedDay) {
                  _focusedDay = focusedDay;
                  _loadEvents();
                },
                calendarStyle: CalendarStyle(
                  outsideDaysVisible: false,
                  weekendTextStyle: TextStyle(color: AppColors.danger.withOpacity(0.7)),
                  todayDecoration: BoxDecoration(
                    color: AppColors.primary.withOpacity(0.12),
                    shape: BoxShape.circle,
                  ),
                  todayTextStyle: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                  selectedDecoration: BoxDecoration(
                    color: AppColors.primary,
                    shape: BoxShape.circle,
                  ),
                  selectedTextStyle: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  defaultTextStyle: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w500),
                  markerDecoration: BoxDecoration(
                    color: AppColors.accentOrange,
                    shape: BoxShape.circle,
                  ),
                  markerSize: 5,
                  markersMaxCount: 3,
                ),
                headerStyle: HeaderStyle(
                  formatButtonVisible: false,
                  titleCentered: true,
                  titleTextStyle: TextStyle(color: AppColors.textPrimary, fontSize: 17, fontWeight: FontWeight.w700),
                  leftChevronIcon: Icon(Icons.chevron_left_rounded, color: AppColors.primary),
                  rightChevronIcon: Icon(Icons.chevron_right_rounded, color: AppColors.primary),
                ),
                daysOfWeekStyle: DaysOfWeekStyle(
                  weekdayStyle: TextStyle(color: AppColors.textMuted, fontWeight: FontWeight.w600, fontSize: 12),
                  weekendStyle: TextStyle(color: AppColors.danger.withOpacity(0.5), fontWeight: FontWeight.w600, fontSize: 12),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Events List
            if (_selectedDay != null) ...[
              Row(children: [
                const Text('📌', style: TextStyle(fontSize: 18)),
                const SizedBox(width: 6),
                Text(DateFormat('M월 d일 EEEE', 'ko').format(_selectedDay!),
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                  child: Text('${selectedEvents.length}건', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
                ),
              ]),
              const SizedBox(height: 12),
              if (selectedEvents.isEmpty)
                NeonGlassCard(
                  glowColor: AppColors.textLight,
                  padding: const EdgeInsets.all(24),
                  child: Center(child: Text("이 날에 예정된 이벤트가 없습니다.", style: TextStyle(color: AppColors.textMuted, fontSize: 14))),
                )
              else
                ...selectedEvents.map((e) => _buildEventCard(e)).toList(),
            ] else ...[
              Center(child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(children: [
                  Icon(Icons.touch_app_rounded, color: AppColors.textLight, size: 40),
                  const SizedBox(height: 12),
                  Text("날짜를 선택해 주세요", style: TextStyle(color: AppColors.textMuted, fontSize: 14)),
                ]),
              )),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildEventCard(dynamic event) {
    int impact = event['impact_score'] ?? 0;
    Color impactColor = impact >= 4 ? AppColors.danger : impact >= 2 ? AppColors.accentOrange : AppColors.success;
    String impactLabel = impact >= 4 ? '높음' : impact >= 2 ? '보통' : '낮음';

    String country = event['country'] ?? '';
    String flag = country == 'US' ? '🇺🇸' : country == 'KR' ? '🇰🇷' : country == 'JP' ? '🇯🇵' : country == 'EU' ? '🇪🇺' : country == 'CN' ? '🇨🇳' : '🌍';

    return NeonGlassCard(
      glowColor: impactColor,
      margin: const EdgeInsets.only(bottom: 10),
      onTap: () => _showEventDetail(event, flag, impactLabel, impactColor),
      padding: const EdgeInsets.all(16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(flag, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(event['title'] ?? '', style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w600)),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: impactColor.withOpacity(0.08), borderRadius: BorderRadius.circular(6)),
                      child: Text('영향: $impactLabel', style: TextStyle(color: impactColor, fontSize: 11, fontWeight: FontWeight.w600)),
                    ),
                    const SizedBox(width: 8),
                    if (event['time'] != null)
                      Text(event['time'], style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                  ],
                ),
                if (event['description'] != null && event['description'].isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text(event['description'], style: TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.4), maxLines: 2, overflow: TextOverflow.ellipsis),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showEventDetail(dynamic event, String flag, String impactLabel, Color impactColor) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppColors.bgSecondary,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Text(flag, style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 8),
            Expanded(child: Text(event['title'] ?? '', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 18))),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(color: impactColor.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                  child: Text('시장 영향: $impactLabel', style: TextStyle(color: impactColor, fontWeight: FontWeight.bold, fontSize: 13)),
                ),
                const SizedBox(width: 12),
                if (event['time'] != null)
                  Text(event['time'], style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              event['description'] ?? '상세 설명이 없습니다.',
              style: TextStyle(color: AppColors.textSecondary, fontSize: 14, height: 1.5),
            ),
            if (event['actual'] != null || event['forecast'] != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: AppColors.bgPrimary, borderRadius: BorderRadius.circular(12)),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildDataColumn("이전", event['previous']),
                    _buildDataColumn("예상", event['forecast']),
                    _buildDataColumn("실제", event['actual'], highlight: true),
                  ],
                ),
              ),
            ],
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text("닫기", style: TextStyle(color: AppColors.primary))),
        ],
      ),
    );
  }

  Widget _buildDataColumn(String label, dynamic value, {bool highlight = false}) {
    return Column(
      children: [
        Text(label, style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
        const SizedBox(height: 4),
        Text(value?.toString() ?? '-', style: TextStyle(color: highlight ? AppColors.textPrimary : AppColors.textSecondary, fontWeight: highlight ? FontWeight.bold : FontWeight.normal, fontSize: 14)),
      ],
    );
  }
}

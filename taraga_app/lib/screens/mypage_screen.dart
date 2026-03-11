import 'dart:async';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class MyPageScreen extends StatefulWidget {
  const MyPageScreen({super.key});
  @override State<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends State<MyPageScreen> {
  final ApiService _apiService = ApiService();
  List<Map<String, dynamic>> _watchlist = [];
  bool _isLoading = true;

  @override
  void initState() { super.initState(); _loadWatchlist(); }

  Future<void> _loadWatchlist() async {
    setState(() => _isLoading = true);
    try {
      final data = await _apiService.getWatchlist();
      if (mounted) setState(() { _watchlist = List<Map<String, dynamic>>.from(data); _isLoading = false; });
    } catch (e) { if (mounted) setState(() { _watchlist = []; _isLoading = false; }); }
  }

  Future<void> _removeFromWatchlist(int itemId, String stockName) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text("관심 종목 삭제"),
        content: Text("'$stockName'을(를) 관심 목록에서 삭제하시겠습니까?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text("취소")),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.danger, foregroundColor: Colors.white),
            child: Text("삭제"),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await _apiService.removeFromWatchlist(itemId);
      _loadWatchlist();
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('삭제 실패: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: MediaQuery.of(context).padding.top + 16),

            // Profile Card
            NeonGlassCard(
              glowColor: AppColors.primary,
              padding: const EdgeInsets.all(24),
              child: Row(children: [
                // Avatar
                Container(
                  padding: const EdgeInsets.all(3),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: AppColors.blueGradient,
                  ),
                  child: Container(
                    width: 60, height: 60,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppColors.bgWhite,
                      border: Border.all(color: AppColors.bgWhite, width: 3),
                    ),
                    child: Icon(Icons.person_rounded, color: AppColors.primary, size: 30),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('투자자님', style: TextStyle(color: AppColors.textPrimary, fontSize: 22, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 4),
                  Row(children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                      child: Text('🌉 Bridge Investor', style: TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.w600)),
                    ),
                  ]),
                ])),
                Container(
                  decoration: BoxDecoration(color: AppColors.bgSecondary, borderRadius: BorderRadius.circular(12)),
                  child: IconButton(
                    icon: Icon(Icons.settings_outlined, color: AppColors.textMuted, size: 20),
                    onPressed: _showSettingsDialog,
                  ),
                ),
              ]),
            ),
            const SizedBox(height: 28),

            // Watchlist Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("내 관심 종목", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  IconButton(
                    onPressed: () => _showSearchDialog(context),
                    icon: Icon(Icons.add_circle_rounded, color: AppColors.primary, size: 28),
                    tooltip: '종목 추가',
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Watchlist Items
            _isLoading
                ? Center(child: CircularProgressIndicator(color: AppColors.primary))
                : _watchlist.isEmpty
                    ? NeonGlassCard(
                        padding: const EdgeInsets.all(32),
                        child: Center(
                          child: Column(
                            children: [
                              Icon(Icons.bookmark_border_rounded, size: 48, color: AppColors.textLight),
                              const SizedBox(height: 16),
                              Text("아직 관심 종목이 없습니다.", style: TextStyle(color: AppColors.textSecondary)),
                              const SizedBox(height: 16),
                              ElevatedButton.icon(
                                onPressed: () => _showSearchDialog(context),
                                icon: Icon(Icons.add),
                                label: Text("종목 찾기"),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.primary,
                                  foregroundColor: Colors.white,
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                ),
                              ),
                            ],
                          ),
                        ),
                      )
                    : Column(
                        children: _watchlist.map((item) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: NeonGlassCard(
                              padding: const EdgeInsets.all(16),
                              child: Row(
                                children: [
                                  Container(
                                    width: 40, height: 40,
                                    alignment: Alignment.center,
                                    decoration: BoxDecoration(color: AppColors.bgSecondary, shape: BoxShape.circle),
                                    child: Text(item['ticker']?[0] ?? '?', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(item['stock_name'] ?? 'Unknown', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: AppColors.textPrimary)),
                                        Text(item['ticker'] ?? '', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                                      ],
                                    ),
                                  ),
                                  IconButton(
                                    icon: Icon(Icons.delete_outline_rounded, color: AppColors.textMuted),
                                    onPressed: () => _removeFromWatchlist(item['id'], item['stock_name'] ?? ''),
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
          ],
        ),
      ),
    );
  }

  void _showSearchDialog(BuildContext context) {
    showDialog(context: context, builder: (context) => SearchStockDialog(
      apiService: _apiService,
      onAdded: _loadWatchlist,
    ));
  }

  void _showSettingsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text("설정", style: TextStyle(fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ListTile(
              leading: Icon(Icons.info_outline),
              title: Text("앱 버전"),
              subtitle: Text("v1.0.0 (Beta)"),
            ),
            ListTile(
              leading: Icon(Icons.notifications_outlined),
              title: Text("알림 설정"),
              trailing: Switch(value: true, onChanged: (v) {}),
            ),
            ListTile(
              leading: Icon(Icons.logout, color: AppColors.danger),
              title: Text("로그아웃", style: TextStyle(color: AppColors.danger)),
              onTap: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("로그아웃 기능은 준비 중입니다.")));
              },
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text("닫기")),
        ],
      ),
    );
  }
}

class SearchStockDialog extends StatefulWidget {
  final ApiService apiService;
  final VoidCallback onAdded;
  const SearchStockDialog({super.key, required this.apiService, required this.onAdded});
  @override State<SearchStockDialog> createState() => _SearchStockDialogState();
}

class _SearchStockDialogState extends State<SearchStockDialog> {
  final TextEditingController _controller = TextEditingController();
  List<Map<String, dynamic>> _searchResults = [];
  bool _isSearching = false;
  Timer? _debounceTimer;

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 400), () {
      _search(query);
    });
  }

  Future<void> _search(String query) async {
    if (query.isEmpty) { setState(() => _searchResults = []); return; }
    setState(() => _isSearching = true);
    try {
      final results = await widget.apiService.searchStock(query);
      if (mounted) setState(() { _searchResults = List<Map<String, dynamic>>.from(results); _isSearching = false; });
    } catch (e) { if (mounted) setState(() => _isSearching = false); }
  }

  Future<void> _add(Map<String, dynamic> result) async {
    try {
      await widget.apiService.addToWatchlist(result['ticker'] ?? '', result['name'] ?? '');
      widget.onAdded();
      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('추가 실패: $e')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: AppColors.bgWhite,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 450, maxHeight: 550),
        padding: const EdgeInsets.all(24),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text("종목 검색", style: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.w700)),
            IconButton(onPressed: () => Navigator.pop(context), icon: Icon(Icons.close_rounded, color: AppColors.textMuted)),
          ]),
          const SizedBox(height: 16),
          TextField(
            controller: _controller,
            onChanged: _onSearchChanged,
            style: TextStyle(color: AppColors.textPrimary),
            decoration: InputDecoration(
              hintText: '종목명 또는 티커 입력',
              hintStyle: TextStyle(color: AppColors.textLight),
              prefixIcon: Icon(Icons.search_rounded, color: AppColors.textMuted),
              filled: true,
              fillColor: AppColors.bgSecondary,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide.none),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(14), borderSide: BorderSide(color: AppColors.primary, width: 1.5)),
            ),
          ),
          const SizedBox(height: 16),
          if (_isSearching)
            Padding(padding: const EdgeInsets.all(20), child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2))
          else
            Flexible(
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: _searchResults.length,
                itemBuilder: (context, index) {
                  final result = _searchResults[index];
                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    decoration: AppDecorations.cleanCard(borderRadius: 12),
                    child: ListTile(
                      onTap: () => _add(result),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      leading: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                        child: Text(result['ticker'] ?? '', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 13)),
                      ),
                      title: Text(result['name'] ?? '', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600)),
                      trailing: Icon(Icons.add_circle_outline_rounded, color: AppColors.primary),
                    ),
                  );
                },
              ),
            ),
        ]),
      ),
    );
  }
}

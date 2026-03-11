import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/bridge_news.dart';
import '../theme/app_theme.dart';

import '../models/value_chain.dart';
import '../widgets/value_chain_card.dart';

class InsightScreen extends StatefulWidget {
  const InsightScreen({super.key});
  @override State<InsightScreen> createState() => _InsightScreenState();
}

class _InsightScreenState extends State<InsightScreen> {
  final ApiService _apiService = ApiService();
  List<dynamic> _personalMatches = [];
  List<BridgeNews> _bridgeNewsList = [];
  ValueChainResponse? _valueChainData;
  bool _isLoadingMatches = true;
  bool _isLoadingNews = true;
  bool _isLoadingValueChain = true;
  String? _errorMessage;

  @override
  void initState() { super.initState(); _loadData(); }

  Future<void> _loadData() async {
    setState(() { 
      _isLoadingMatches = true; 
      _isLoadingNews = true; 
      _isLoadingValueChain = true; 
      _errorMessage = null; 
    });

    try {
      final matchesData = await _apiService.getPersonalMatches();
      if (mounted) setState(() { _personalMatches = matchesData['personal_matches'] ?? []; _isLoadingMatches = false; });
    } catch (_) { if (mounted) setState(() { _personalMatches = []; _isLoadingMatches = false; }); }

    try {
      final newsList = await _apiService.getBridgeNews();
      if (mounted) setState(() { _bridgeNewsList = newsList; _isLoadingNews = false; });
    } catch (e) { if (mounted) setState(() { _errorMessage = e.toString(); _isLoadingNews = false; }); }

    try {
      // 1. Get themes list
      final themes = await _apiService.getThemes();
      if (themes.isNotEmpty) {
        // 2. Get value chain for the first theme (placeholder logic)
        // In future, we can add a selector UI
        final valueChain = await _apiService.getValueChain(themes.first.id);
        if (mounted) setState(() { _valueChainData = valueChain; _isLoadingValueChain = false; });
      } else {
        if (mounted) setState(() { _isLoadingValueChain = false; });
      }
    } catch (e) {
      if (mounted) setState(() { _isLoadingValueChain = false; });
      print("Error loading value chain: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: RefreshIndicator(
        color: AppColors.primary,
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 100),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(height: MediaQuery.of(context).padding.top + 16),
              // Header
              Row(children: [
                const Text('💡', style: TextStyle(fontSize: 24)),
                const SizedBox(width: 8),
                Text('인사이트', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.textPrimary, letterSpacing: -0.5)),
              ]),
              const SizedBox(height: 8),
              Text('미국발 뉴스가 한국 시장에 미치는 영향을 분석합니다.', style: TextStyle(color: AppColors.textMuted, fontSize: 14)),
              const SizedBox(height: 28),

              // Personal Matches Section
              _buildSectionHeader('🎯', '나의 종목 매칭'),
              const SizedBox(height: 12),
              _isLoadingMatches
                  ? Center(child: Padding(padding: const EdgeInsets.all(32), child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)))
                  : _personalMatches.isEmpty
                      ? _buildEmptyCard("매칭되는 종목이 없습니다.\n마이페이지에서 관심 종목을 추가하세요.")
                      : Column(children: _personalMatches.map((match) => _buildMatchCard(match)).toList()),
              const SizedBox(height: 28),

              // Bridge News Section
              _buildSectionHeader('🌉', '브릿지 뉴스 (US→KR)'),
              const SizedBox(height: 12),
              _isLoadingNews
                  ? Center(child: Padding(padding: const EdgeInsets.all(32), child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)))
                  : _errorMessage != null
                      ? _buildErrorCard()
                      : _buildBridgeNewsSection(),
              const SizedBox(height: 28),

              // Value Chain Section
              _buildSectionHeader('🔗', '밸류체인'),
              const SizedBox(height: 12),
              _isLoadingValueChain
                  ? Center(child: Padding(padding: const EdgeInsets.all(32), child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)))
                  : _valueChainData != null
                      ? ValueChainCard(valueChain: _valueChainData!)
                      : _buildEmptyCard("데이터를 불러올 수 없습니다."),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String emoji, String title) {
    return Row(children: [
      Text(emoji, style: const TextStyle(fontSize: 20)),
      const SizedBox(width: 6),
      Text(title, style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
    ]);
  }

  Widget _buildEmptyCard(String message) {
    return NeonGlassCard(
      glowColor: AppColors.textLight,
      padding: const EdgeInsets.all(32),
      child: Center(child: Text(message, textAlign: TextAlign.center, style: TextStyle(color: AppColors.textMuted, fontSize: 14, height: 1.5))),
    );
  }

  Widget _buildErrorCard() {
    return NeonGlassCard(
      glowColor: AppColors.danger,
      padding: const EdgeInsets.all(24),
      child: Column(children: [
        Icon(Icons.error_outline_rounded, color: AppColors.danger, size: 40),
        const SizedBox(height: 12),
        Text('뉴스를 불러오지 못했습니다.', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600)),
        const SizedBox(height: 12),
        ElevatedButton(onPressed: _loadData,
          style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
          child: const Text('재시도')),
      ]),
    );
  }

  Widget _buildMatchCard(Map<String, dynamic> match) {
    bool isPositive = (match['us_change_percent'] ?? 0) >= 0;
    final accentColor = isPositive ? AppColors.success : AppColors.danger;

    return NeonGlassCard(
      glowColor: accentColor,
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Row(children: [
            Icon(Icons.public_rounded, color: AppColors.primary, size: 18),
            const SizedBox(width: 8),
            Text(match['theme_name'], style: TextStyle(color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w600)),
          ]),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(color: accentColor.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
            child: Text('${isPositive ? '+' : ''}${match['us_change_percent']}%', style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        ]),
        const SizedBox(height: 8),
        Text('${match['reason']}', style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
        if (match['my_stocks'] != null) ...[
          const SizedBox(height: 10),
          Wrap(spacing: 8, runSpacing: 6,
            children: (match['my_stocks'] as List).map((s) => Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
              decoration: BoxDecoration(color: accentColor.withOpacity(0.06), borderRadius: BorderRadius.circular(8), border: Border.all(color: accentColor.withOpacity(0.15))),
              child: Text('${s['name']}', style: TextStyle(color: accentColor, fontSize: 12, fontWeight: FontWeight.w600)),
            )).toList(),
          ),
        ],
      ]),
    );
  }

  Widget _buildBridgeNewsSection() {
    if (_bridgeNewsList.isEmpty) return _buildEmptyCard("브릿지 뉴스가 없습니다.");
    return Column(children: _bridgeNewsList.map((news) => _buildBridgeNewsCard(news)).toList());
  }

  Widget _buildBridgeNewsCard(BridgeNews news) {
    return NeonGlassCard(
      glowColor: AppColors.primary,
      margin: const EdgeInsets.only(bottom: 14),
      onTap: () => _showNewsDetail(news),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // US section
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(color: AppColors.bgBlueLight, borderRadius: const BorderRadius.vertical(top: Radius.circular(16))),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Text("🇺🇸", style: const TextStyle(fontSize: 18)),
              const SizedBox(width: 8),
              Expanded(child: Text(news.usHeadline, style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w600), maxLines: 2, overflow: TextOverflow.ellipsis)),
            ]),
            if (news.usSource.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(news.usSource, style: TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.5), maxLines: 3, overflow: TextOverflow.ellipsis),
            ],
          ]),
        ),
        // Bridge arrow
        Container(
          width: double.infinity, padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            Container(width: 60, height: 1, color: AppColors.border),
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 12),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(color: AppColors.accentOrange.withOpacity(0.1), borderRadius: BorderRadius.circular(20), border: Border.all(color: AppColors.accentOrange.withOpacity(0.2))),
              child: Row(children: [
                Text("🌉", style: const TextStyle(fontSize: 14)),
                const SizedBox(width: 4),
                Icon(Icons.arrow_downward_rounded, color: AppColors.accentOrange, size: 16),
              ]),
            ),
            Container(width: 60, height: 1, color: AppColors.border),
          ]),
        ),
        // KR Impact
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              Text("🇰🇷", style: const TextStyle(fontSize: 18)),
              const SizedBox(width: 8),
              Expanded(child: Text("한국 영향 분석", style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w600))),
            ]),
            const SizedBox(height: 8),
            Text(news.krImpact, style: TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.5)),
            if (news.relatedStocks.isNotEmpty) ...[
              const SizedBox(height: 12),
              Wrap(spacing: 6, runSpacing: 6,
                children: news.relatedStocks.map((s) => InkWell(
                  onTap: () => _showAddStockDialog(s.ticker, s.name),
                  borderRadius: BorderRadius.circular(8),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(color: AppColors.primary.withOpacity(0.06), borderRadius: BorderRadius.circular(8), border: Border.all(color: AppColors.primary.withOpacity(0.15))),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('${s.name} (${s.ticker})', style: TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.w600)),
                        const SizedBox(width: 4),
                        Icon(Icons.add_circle_outline, size: 12, color: AppColors.primary.withOpacity(0.6))
                      ],
                    ),
                  ),
                )).toList(),
              ),
            ],
          ]),
        ),
      ]),
    );
  }

  void _showNewsDetail(BridgeNews news) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        builder: (_, controller) => Container(
          decoration: BoxDecoration(
            color: AppColors.bgWhite,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
            children: [
              // Header with Close Button
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Container(
                      width: 40, height: 4,
                      decoration: BoxDecoration(color: AppColors.border, borderRadius: BorderRadius.circular(2)),
                    ),
                    Align(
                      alignment: Alignment.centerRight,
                      child: IconButton(
                        icon: const Icon(Icons.close_rounded, color: AppColors.textMuted),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView(
                  controller: controller,
                  padding: const EdgeInsets.all(24),
                  children: [
                    Text("🇺🇸 US Market", style: TextStyle(color: AppColors.textMuted, fontWeight: FontWeight.bold, fontSize: 13)),
                    const SizedBox(height: 8),
                    Text(news.usHeadline, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                    const SizedBox(height: 8),
                    Text(news.usSource, style: TextStyle(fontSize: 15, color: AppColors.textSecondary, height: 1.6)),
                    Divider(height: 40, color: AppColors.divider),
                    Text("🇰🇷 Korea Impact", style: TextStyle(color: AppColors.accentOrange, fontWeight: FontWeight.bold, fontSize: 13)),
                    const SizedBox(height: 8),
                    Text(news.krImpact, style: TextStyle(fontSize: 16, color: AppColors.textPrimary, height: 1.6)),
                    const SizedBox(height: 24),
                    Text("관련 종목", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                    const SizedBox(height: 12),
                    Wrap(spacing: 8, runSpacing: 8,
                      children: news.relatedStocks.map((s) => ActionChip(
                        avatar: CircleAvatar(backgroundColor: AppColors.primary.withOpacity(0.2), child: Text(s.ticker[0], style: TextStyle(fontSize: 10, color: AppColors.primary))),
                        label: Text(s.name),
                        backgroundColor: AppColors.bgSecondary,
                        side: BorderSide.none,
                        onPressed: () => _showAddStockDialog(s.ticker, s.name),
                      )).toList(),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showAddStockDialog(String ticker, String name) {
    showDialog(
      context: context, 
      builder: (context) => AlertDialog(
        title: Text("관심 종목 추가"),
        content: Text("'$name' ($ticker) 종목을 관심 목록에 추가하시겠습니까?"),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text("취소")),
          ElevatedButton(
            onPressed: () async {
              try {
                await _apiService.addToWatchlist(ticker, name);
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("'$name' 추가 완료!")));
                }
              } catch (e) {
                if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("오류: $e")));
              }
            },
            child: Text("추가"),
          ),
        ],
      ),
    );
  }
}

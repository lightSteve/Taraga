import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../services/api_service.dart';
import '../models/theme.dart';
import '../models/stock.dart';
import '../models/briefing.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import 'package:chart_sparkline/chart_sparkline.dart';
import '../theme/app_theme.dart';
import 'theme_detail_screen.dart';
import 'stock_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  List<MarketTheme> _themes = [];
  List<dynamic> _personalMatches = [];
  List<Stock> _gainers = [];
  List<Stock> _losers = [];
  bool _isLoading = true;
  String? _errorMessage;
  Map<String, dynamic>? _appMode;
  Map<String, dynamic>? _marketIndices;
  Briefing? _briefing;

  // New State: Selected Market Region
  String _selectedMarket = "US"; // Default US

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() { _isLoading = true; _errorMessage = null; });
    
    try {
      // 1. Get App Mode (Critical)
      try {
        _appMode = await _apiService.getAppMode();
      } catch (e) {
        print("Error loading app mode: $e");
      }

      // 2. Get Themes
      try {
        _themes = await _apiService.getThemes();
      } catch (e) {
        print("Error loading themes: $e");
        // Fallback or empty
      }

      // 3. Get Personal Matches (Handle 404/Error gracefully)
      try {
        final matchesData = await _apiService.getPersonalMatches();
        _personalMatches = matchesData['personal_matches'] ?? [];
      } catch (e) {
        print("Error loading matches: $e");
      }

      // 4. Get Market Movers
      try {
        final movers = await _apiService.getUSMarketMovers();
        _gainers = movers['gainers'] ?? [];
        _losers = movers['losers'] ?? [];
      } catch (e) {
        print("Error loading movers: $e");
      }

      // 5. Get Indices
      try {
        _marketIndices = await _apiService.getMarketIndices();
        print("DEBUG: Indices loaded: $_marketIndices");
      } catch (e) {
        print("Error loading indices: $e");
      }

      // 6. Get Briefing
      try {
         _briefing = await _apiService.getTodayBriefing();
      } catch (e) {
        print("Error loading briefing: $e");
      }

      setState(() {
        _isLoading = false;
      });

    } catch (e) {
      // Catch major unknown errors
      print("Major error in _loadData: $e");
      setState(() { _errorMessage = e.toString(); _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgPrimary,
      body: CustomScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        slivers: [
          // ─── App Bar ───
          SliverAppBar(
            floating: true,
            pinned: false,
            backgroundColor: AppColors.bgPrimary,
            elevation: 0,
            expandedHeight: 60,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                padding: const EdgeInsets.fromLTRB(20, 0, 12, 0),
                alignment: Alignment.bottomCenter,
                child: Row(
                  children: [
                    const Text('🌉 ', style: TextStyle(fontSize: 24)),
                    Text(
                      'Taraga',
                      style: TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        color: AppColors.textPrimary,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primaryLight,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        '따라가',
                        style: TextStyle(
                          color: AppColors.primary,
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1,
                        ),
                      ),
                    ),
                    const Spacer(),
                    _buildAppBarIcon(Icons.notifications_outlined, () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: const Text('알림 기능 준비 중입니다.'), backgroundColor: AppColors.textPrimary),
                      );
                    }),
                    _buildAppBarIcon(Icons.refresh_rounded, _loadData),
                  ],
                ),
              ),
            ),
          ),

          // ─── Body ───
          if (_isLoading)
            SliverFillRemaining(
              child: Center(child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5)),
            )
          else if (_errorMessage != null)
            SliverFillRemaining(child: _buildErrorView())
          else
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 100),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  if (_marketIndices != null) _buildMarketWeatherCard(),
                  const SizedBox(height: 20),
                  _buildBriefingCard(),
                  const SizedBox(height: 24),
                  if (_personalMatches.isNotEmpty) ...[
                    _buildPersonalMatchesSection(),
                    const SizedBox(height: 24),
                  ],
                  _buildBurgerVsWallStreet(),
                  const SizedBox(height: 24),
                  _buildThemesSection(),
                  const SizedBox(height: 24),
                  MarketMoversWidget(gainers: _gainers, losers: _losers),
                  const SizedBox(height: 24),
                ]),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildAppBarIcon(IconData icon, VoidCallback onPressed) {
    return Container(
      margin: const EdgeInsets.only(left: 4),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        borderRadius: BorderRadius.circular(12),
      ),
      child: IconButton(
        icon: Icon(icon, color: AppColors.textMuted, size: 20),
        onPressed: onPressed,
        splashRadius: 20,
      ),
    );
  }

  Widget _buildBriefingCard() {
    // 1. Helper Logic
    String getChange(String ticker) {
      if (_marketIndices == null || !_marketIndices!.containsKey(ticker)) return "0.0%";
      double val = (_marketIndices![ticker]['regularMarketChangePercent'] ?? 0.0).toDouble();
      return "${val >= 0 ? '+' : ''}${val.toStringAsFixed(2)}%";
    }

    Color getColor(String ticker) {
      if (_marketIndices == null || !_marketIndices!.containsKey(ticker)) return AppColors.textMuted;
      double val = (_marketIndices![ticker]['regularMarketChangePercent'] ?? 0.0).toDouble();
      return val >= 0 ? AppColors.marketUp : AppColors.marketDown;
    }

    List<double> getHistory(String ticker) {
      if (_marketIndices == null || !_marketIndices!.containsKey(ticker)) return [0.0, 0.0];
      try {
        List<dynamic> history = _marketIndices![ticker]['history'] ?? [];
        if (history.isEmpty) return [0.0, 0.0];
        return history.map((e) => (e as num).toDouble()).toList();
      } catch (e) {
        return [0.0, 0.0];
      }
    }

    // 2. Identify Hot Market
    String hotMarket = "US";
    double maxAvgChange = -999.0;
    
    Map<String, List<String>> markets = {
      "US": ["S&P 500", "Nasdaq", "Dow Jones"],
      "KR": ["KOSPI", "KOSDAQ"],
      "Coin": ["Bitcoin", "Ethereum"]
    };

    if (_marketIndices != null) {
      markets.forEach((market, tickers) {
        double totalChange = 0;
        int count = 0;
        for (var t in tickers) {
          if (_marketIndices!.containsKey(t)) {
             totalChange += (_marketIndices![t]['regularMarketChangePercent'] ?? _marketIndices![t]['change_percent'] ?? 0.0) as double;
             count++;
          }
        }
        if (count > 0) {
          double avg = totalChange / count;
          if (avg > maxAvgChange) {
            maxAvgChange = avg;
            hotMarket = market;
          }
        }
      });
    }

    return _GlobalMarketCard(
      marketIndices: _marketIndices,
      hotMarket: hotMarket,
      getChange: getChange,
      getColor: getColor,
      getHistory: getHistory,
      selectedMarket: _selectedMarket,
      onTabChanged: (index) {
        final markets = ["US", "KR", "Coin"];
        if (index >= 0 && index < markets.length) {
          setState(() {
            _selectedMarket = markets[index];
          });
        }
      },
    );
  }


  Widget _buildThemesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                const Text('🔥', style: TextStyle(fontSize: 20)),
                const SizedBox(width: 6),
                Text('지금 뜨는 테마', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.accentOrange.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text('${_themes.length} 테마',
                style: TextStyle(color: AppColors.accentOrange, fontSize: 12, fontWeight: FontWeight.w600)),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 1.6,
          ),
          itemCount: _themes.length,
          itemBuilder: (context, index) => _buildThemeGridCard(_themes[index], index),
        ),
      ],
    );
  }

  Widget _buildThemeGridCard(MarketTheme theme, int index) {
    final colorSets = [
      [AppColors.primary, AppColors.primaryLight],
      [AppColors.accentPurple, const Color(0xFFEDE7FF)],
      [AppColors.accentGreen, const Color(0xFFE0F8EE)],
      [AppColors.accentOrange, const Color(0xFFFFF3E0)],
    ];
    final colors = colorSets[index % colorSets.length];

    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ThemeDetailScreen(theme: theme))),
        child: Container(
          decoration: BoxDecoration(
            color: colors[1],
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: colors[0].withOpacity(0.15), width: 1),
          ),
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Icon(Icons.trending_up_rounded, color: colors[0], size: 20),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: colors[0].withOpacity(0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      theme.keywords.isNotEmpty ? theme.keywords.first : '',
                      style: TextStyle(color: colors[0], fontWeight: FontWeight.bold, fontSize: 12),
                      maxLines: 1, overflow: TextOverflow.ellipsis),
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(theme.name, style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w700),
                    maxLines: 1, overflow: TextOverflow.ellipsis),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPersonalMatchesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('🎯', style: TextStyle(fontSize: 20)),
            const SizedBox(width: 6),
            Text('내 종목 분석', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
          ],
        ),
        const SizedBox(height: 12),
        ..._personalMatches.map((group) => _buildGroupedMatchCard(group)).toList(),
      ],
    );
  }

  Widget _buildGroupedMatchCard(Map<String, dynamic> group) {
    bool isPositive = (group['us_change_percent'] ?? 0) >= 0;
    final accentColor = isPositive ? AppColors.marketUp : AppColors.marketDown;

    return NeonGlassCard(
      glowColor: accentColor,
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(children: [
                  Icon(Icons.public_rounded, color: AppColors.primary, size: 20),
                  const SizedBox(width: 8),
                  Text(group['theme_name'], style: TextStyle(color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.w700)),
                ]),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: accentColor.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text('${isPositive ? '+' : ''}${group['us_change_percent']}%',
                    style: TextStyle(color: accentColor, fontWeight: FontWeight.bold, fontSize: 13)),
                ),
              ],
            ),
          ),
          Divider(color: AppColors.divider, height: 1),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Text("원인: ${group['reason']}", style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
          ),
          Divider(color: AppColors.divider, height: 1),
          ListView.separated(
            shrinkWrap: true, physics: const NeverScrollableScrollPhysics(),
            itemCount: (group['my_stocks'] as List).length,
            separatorBuilder: (_, __) => Divider(color: AppColors.divider, height: 1),
            itemBuilder: (context, index) {
              final stock = group['my_stocks'][index];
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(children: [
                      NeonDot(color: accentColor, size: 5),
                      const SizedBox(width: 12),
                      Text(stock['name'], style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w500)),
                      const SizedBox(width: 8),
                      Text(stock['ticker'], style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                    ]),
                    Row(children: [
                      Icon(Icons.trending_up, color: accentColor, size: 16),
                      const SizedBox(width: 4),
                      Text("상승 예상", style: TextStyle(color: accentColor, fontSize: 12, fontWeight: FontWeight.w600)),
                    ]),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildBurgerVsWallStreet() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              "🍔",
              style: const TextStyle(fontSize: 20),
            ),
            const SizedBox(width: 6),
            Text(
              "🍔 버거형 vs 🏦 월가",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Text(
          "핫 트렌드 비교",
          style: TextStyle(color: AppColors.textMuted, fontSize: 13),
        ),
        const SizedBox(height: 14),
        if (_selectedMarket == "US")
          _BurgerVsWallStreetSlider(
            key: ValueKey(_selectedMarket),
            apiService: _apiService, 
            selectedRegion: _selectedMarket
          )
        else
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Text(
                _selectedMarket == "KR" ? "한국 시장 개미/기관 데이터는 현재 지원되지 않습니다." : "코인 커뮤니티/고래 데이터는 현재 지원되지 않습니다.",
                style: TextStyle(color: AppColors.textMuted, fontSize: 14),
              ),
            ),
          ),
      ],
    );
  }
}

// ─── Burger vs Wall Street Slider ───
class _BurgerVsWallStreetSlider extends StatefulWidget {
  final ApiService apiService;
  final String selectedRegion;
  const _BurgerVsWallStreetSlider({super.key, required this.apiService, required this.selectedRegion});
  @override State<_BurgerVsWallStreetSlider> createState() => _BurgerVsWallStreetSliderState();
}

class _BurgerVsWallStreetSliderState extends State<_BurgerVsWallStreetSlider> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  Timer? _autoScrollTimer;

  List<dynamic>? _retailPicksData;
  List<dynamic>? _institutionalPicksData;
  bool _isLoadingRetail = true;
  bool _isLoadingInstitutional = true;

  @override void initState() { super.initState(); _startAutoScroll(); _loadData(); }

  @override
  void didUpdateWidget(_BurgerVsWallStreetSlider oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedRegion != widget.selectedRegion) {
      _loadData();
    }
  }

  Future<void> _loadData() async {
    setState(() { _isLoadingRetail = true; _isLoadingInstitutional = true; });
    widget.apiService.getRetailPicks(region: widget.selectedRegion).then((data) {
      if (mounted) setState(() { _retailPicksData = data; _isLoadingRetail = false; });
    }).catchError((e) { if (mounted) setState(() { _retailPicksData = []; _isLoadingRetail = false; }); });

    widget.apiService.getInstitutionalPicks(region: widget.selectedRegion).then((data) {
      if (mounted) setState(() { _institutionalPicksData = data; _isLoadingInstitutional = false; });
    }).catchError((e) { if (mounted) setState(() { _institutionalPicksData = []; _isLoadingInstitutional = false; }); });
  }

  @override void dispose() { _autoScrollTimer?.cancel(); _pageController.dispose(); super.dispose(); }

  void _startAutoScroll() {
    _autoScrollTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (_pageController.hasClients) {
        _pageController.animateToPage((_currentPage + 1) % 2, duration: const Duration(milliseconds: 500), curve: Curves.easeInOut);
      }
    });
  }
  void _resetTimer() { _autoScrollTimer?.cancel(); _startAutoScroll(); }
  void _goToPage(int page) { _resetTimer(); _pageController.animateToPage(page, duration: const Duration(milliseconds: 300), curve: Curves.easeInOut); }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          height: 290,
          child: PageView(
            controller: _pageController,
            onPageChanged: (i) { setState(() => _currentPage = i); _resetTimer(); },
            children: [
              _buildTrendCard(
                title: widget.selectedRegion == "Coin" ? "🪙 커뮤니티 픽" : (widget.selectedRegion == "KR" ? "🐜 개미들의 선택" : "🍔 버거형들의 원픽"), 
                subtitle: widget.selectedRegion == "Coin" ? "밈코인 급등주" : (widget.selectedRegion == "KR" ? "실시간 인기 검색" : "커뮤니티(WSB) 급등 언급"), 
                icon: widget.selectedRegion == "Coin" ? "🔥" : (widget.selectedRegion == "KR" ? "🐜" : "🍔"),
                color: AppColors.accentOrange, items: _retailPicksData, isLoading: _isLoadingRetail, isRetail: true),
              _buildTrendCard(
                title: widget.selectedRegion == "Coin" ? "🐋 고래들의 선택" : (widget.selectedRegion == "KR" ? "🏦 기관/외인 픽" : "🏦 월가 강력 매수"), 
                subtitle: widget.selectedRegion == "Coin" ? "대량 매집 포착" : (widget.selectedRegion == "KR" ? "순매수 상위 종목" : "애널리스트 등급 상향"), 
                icon: widget.selectedRegion == "Coin" ? "🐋" : (widget.selectedRegion == "KR" ? "🏦" : "🏦"),
                color: AppColors.primary, items: _institutionalPicksData, isLoading: _isLoadingInstitutional, isRetail: false),
            ],
          ),
        ),
        const SizedBox(height: 14),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(2, (i) {
            final isActive = _currentPage == i;
            final color = i == 0 ? AppColors.accentOrange : AppColors.primary;
            return GestureDetector(
              onTap: () => _goToPage(i),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: isActive ? 24 : 8, height: 8,
                decoration: BoxDecoration(
                  color: isActive ? color : AppColors.border,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            );
          }),
        ),
      ],
    );
  }

  Widget _buildTrendCard({
    required String title, required String subtitle, required String icon, required Color color,
    required List<dynamic>? items, required bool isLoading, required bool isRetail,
  }) {
    return InkWell(
      onTap: () { if (items != null && items.isNotEmpty) _showTrendDetailsDialog(context: context, title: title, subtitle: subtitle, icon: icon, color: color, items: items, isRetail: isRetail); },
      borderRadius: BorderRadius.circular(16),
      child: NeonGlassCard(
        glowColor: color,
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Text(icon, style: const TextStyle(fontSize: 32)),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w700, fontSize: 17), maxLines: 1, overflow: TextOverflow.ellipsis),
                Text(subtitle, style: TextStyle(color: AppColors.textMuted, fontSize: 13), maxLines: 1, overflow: TextOverflow.ellipsis),
              ])),
              Icon(Icons.touch_app_rounded, color: color.withOpacity(0.3), size: 18),
            ]),
            Divider(color: AppColors.divider, height: 24),
            SizedBox(
              height: 160,
              child: isLoading
                  ? Center(child: CircularProgressIndicator(strokeWidth: 2, color: color))
                  : (items == null || items.isEmpty)
                      ? Center(child: Text("데이터 로딩 중...", style: TextStyle(color: AppColors.textMuted)))
                      : ListView.builder(
                          shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), padding: EdgeInsets.zero,
                          itemCount: items.take(3).length,
                          itemBuilder: (context, index) {
                            final item = items[index];
                            final cp = item['change_percent'] ?? 0.0;
                            final isETF = item['type'] == 'ETF';
                            String emoji = cp > 2 ? '🔥' : cp > 0 ? '☀️' : cp > -2 ? '☁️' : '🌧️';
                            Color cc = cp > 0 ? AppColors.success : cp > -2 ? AppColors.textMuted : AppColors.danger;

                            return InkWell(
                              onTap: () {
                                Navigator.push(context, MaterialPageRoute(
                                  builder: (_) => StockDetailScreen(ticker: item['ticker'] ?? '', name: item['name'] ?? ''),
                                ));
                              },
                              child: Padding(
                                padding: EdgeInsets.only(bottom: index < 2 ? 14.0 : 0),
                                child: Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(flex: 3, child: Row(children: [
                                      Column(children: [
                                        Container(
                                          constraints: const BoxConstraints(minWidth: 50, maxWidth: 65),
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                                          decoration: BoxDecoration(color: color.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                                          child: Text(item['ticker'] ?? '', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13), textAlign: TextAlign.center, maxLines: 1, overflow: TextOverflow.ellipsis),
                                        ),
                                        if (isETF) Container(
                                          margin: const EdgeInsets.only(top: 2),
                                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                          decoration: BoxDecoration(color: AppColors.accentPurple.withOpacity(0.1), borderRadius: BorderRadius.circular(4)),
                                          child: Text('ETF', style: TextStyle(color: AppColors.accentPurple, fontSize: 7, fontWeight: FontWeight.bold)),
                                        ),
                                      ]),
                                      const SizedBox(width: 10),
                                      Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                        Text(item['name'] ?? '', style: TextStyle(color: AppColors.textPrimary, fontSize: 14, fontWeight: FontWeight.w600), maxLines: 1, overflow: TextOverflow.ellipsis),
                                        Row(children: [
                                          Text(emoji, style: const TextStyle(fontSize: 12)),
                                          const SizedBox(width: 4),
                                          Text('${cp > 0 ? '+' : ''}${cp.toStringAsFixed(1)}%', style: TextStyle(color: cc, fontSize: 11, fontWeight: FontWeight.w600)),
                                        ]),
                                      ])),
                                    ])),
                                    const SizedBox(width: 8),
                                    Flexible(flex: 2, child: Text(
                                      isRetail ? (item['mentions'] ?? '') : (item['rating'] ?? '').replaceAll('Upgrade to ', ''),
                                      style: TextStyle(color: AppColors.textMuted, fontSize: 11), textAlign: TextAlign.right, maxLines: 1, overflow: TextOverflow.ellipsis,
                                    )),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  void _showTrendDetailsDialog({required BuildContext context, required String title, required String subtitle, required String icon, required Color color, required List<dynamic> items, required bool isRetail}) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: AppColors.bgWhite,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 500, maxHeight: 600),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                Text(icon, style: const TextStyle(fontSize: 32)),
                const SizedBox(width: 12),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(title, style: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.w700)),
                  Text(subtitle, style: TextStyle(color: AppColors.textMuted, fontSize: 14)),
                ])),
                IconButton(onPressed: () => Navigator.pop(context), icon: Icon(Icons.close_rounded, color: AppColors.textMuted)),
              ]),
              Divider(color: AppColors.divider, height: 32),
              Flexible(
                child: ListView.builder(
                  shrinkWrap: true, itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return InkWell(
                      onTap: () {
                        Navigator.push(context, MaterialPageRoute(
                          builder: (_) => StockDetailScreen(ticker: item['ticker'] ?? '', name: item['name'] ?? ''),
                        ));
                      },
                      borderRadius: BorderRadius.circular(14),
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: AppDecorations.accentCard(accentColor: color, borderRadius: 14),
                        child: Row(children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(color: color.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                            child: Text(item['ticker'] ?? '', style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 14)),
                          ),
                          const SizedBox(width: 12),
                          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Text(item['name'] ?? '', style: TextStyle(color: AppColors.textPrimary, fontSize: 15, fontWeight: FontWeight.w600)),
                            const SizedBox(height: 4),
                            Text(isRetail ? '📈 ${item['mentions'] ?? ''}' : '💼 ${item['rating'] ?? ''}', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
                          ])),
                        ]),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Market Weather + Error View ───
extension _HomeScreenMethods on _HomeScreenState {
  Widget _buildFearGreedGauge() {
    final fgScore = (_briefing?.fearGreedScore ?? 50).toDouble();
    String label;
    if (fgScore >= 75) { label = '극도의\n탐욕'; }
    else if (fgScore >= 55) { label = '${fgScore.toInt()}\n탐욕'; }
    else if (fgScore >= 45) { label = '${fgScore.toInt()}\n중립'; }
    else if (fgScore >= 25) { label = '${fgScore.toInt()}\n공포'; }
    else { label = '극도의\n공포'; }

    Color gaugeColor;
    if (fgScore >= 75) gaugeColor = AppColors.success;
    else if (fgScore >= 55) gaugeColor = AppColors.accentGreen;
    else if (fgScore >= 45) gaugeColor = AppColors.accentOrange;
    else if (fgScore >= 25) gaugeColor = AppColors.danger;
    else gaugeColor = AppColors.danger;

    return SfRadialGauge(
      axes: <RadialAxis>[
        RadialAxis(
          minimum: 0, maximum: 100, showLabels: false, showTicks: false,
          axisLineStyle: AxisLineStyle(
            thickness: 0.2,
            cornerStyle: CornerStyle.bothCurve,
            color: AppColors.border,
            thicknessUnit: GaugeSizeUnit.factor,
          ),
          pointers: <GaugePointer>[
            RangePointer(
              value: fgScore, cornerStyle: CornerStyle.bothCurve,
              width: 0.2, sizeUnit: GaugeSizeUnit.factor,
              gradient: SweepGradient(colors: [gaugeColor, gaugeColor.withOpacity(0.6)]),
            ),
          ],
          annotations: <GaugeAnnotation>[
            GaugeAnnotation(
              positionFactor: 0.1, angle: 90,
              widget: Text(label, textAlign: TextAlign.center,
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMarketWeatherCard() {
    double cp = 0.0;
    if (_marketIndices != null && _marketIndices!.containsKey('S&P 500')) {
       final val = _marketIndices!['S&P 500']['regularMarketChangePercent'];
       if (val != null) {
         cp = (val is num) ? val.toDouble() : 0.0;
       }
    }

    String emoji, title, message;
    Color accentColor;
    Color bgColor;

    if (cp >= 1.0) {
      emoji = "🔥"; title = "Fires (불장)"; message = "뜨거운 불장입니다! 테마주에 주목하세요.";
      accentColor = AppColors.danger; bgColor = const Color(0xFFFFF0EF);
    } else if (cp >= 0.0) {
      emoji = "☀️"; title = "Sunny (맑음)"; message = "시장이 맑습니다. 완만한 상승세.";
      accentColor = AppColors.accentOrange; bgColor = const Color(0xFFFFF6EB);
    } else if (cp >= -1.0) {
      emoji = "☁️"; title = "Cloudy (흐림)"; message = "다소 흐린 장세입니다. 관망이 필요해요.";
      accentColor = AppColors.textMuted; bgColor = AppColors.bgSecondary;
    } else {
      emoji = "☔"; title = "Rain (비)"; message = "비가 내립니다. 리스크 관리가 필수입니다.";
      accentColor = AppColors.primary; bgColor = AppColors.bgBlueLight;
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: accentColor.withOpacity(0.15), width: 1),
      ),
      child: Stack(
        children: [
          Positioned(right: -20, top: -20, child: Icon(Icons.cloud, size: 120, color: accentColor.withOpacity(0.06))),
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(children: [
              Text(emoji, style: const TextStyle(fontSize: 48)),
              const SizedBox(width: 16),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.w700)),
                const SizedBox(height: 4),
                Text(message, style: TextStyle(color: AppColors.textSecondary, fontSize: 13), maxLines: 2),
              ])),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: AppColors.bgWhite, borderRadius: BorderRadius.circular(10), border: Border.all(color: AppColors.border)),
                child: Column(children: [
                  Text("S&P 500", style: TextStyle(color: AppColors.textMuted, fontSize: 10)),
                  Text("${cp >= 0 ? '+' : ''}${cp.toStringAsFixed(2)}%",
                    style: TextStyle(color: cp >= 0 ? AppColors.success : AppColors.danger, fontWeight: FontWeight.bold, fontSize: 14)),
                ]),
              ),
            ]),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: AppColors.danger.withOpacity(0.08), shape: BoxShape.circle),
          child: Icon(Icons.error_outline_rounded, color: AppColors.danger, size: 48)),
        const SizedBox(height: 20),
        Text('데이터 로딩 오류', style: TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.w600)),
        Padding(padding: const EdgeInsets.all(16), child: Text(_errorMessage!, textAlign: TextAlign.center, style: TextStyle(color: AppColors.textMuted))),
        ElevatedButton(
          onPressed: _loadData,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.primary, foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 12),
          ),
          child: const Text('재시도', style: TextStyle(fontWeight: FontWeight.w600)),
        ),
      ]),
    );
  }
}

// ─── Market Movers ───
class MarketMoversWidget extends StatefulWidget {
  final List<Stock> gainers;
  final List<Stock> losers;
  const MarketMoversWidget({super.key, required this.gainers, required this.losers});
  @override State<MarketMoversWidget> createState() => _MarketMoversWidgetState();
}

class _MarketMoversWidgetState extends State<MarketMoversWidget> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isExpanded = false;

  @override void initState() { super.initState(); _tabController = TabController(length: 2, vsync: this); }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          const Text('📊', style: TextStyle(fontSize: 20)),
          const SizedBox(width: 6),
          Text('시장 급등락', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
        ]),
        const SizedBox(height: 14),
        NeonGlassCard(
          glowColor: AppColors.primary,
          child: Column(children: [
            TabBar(
              controller: _tabController,
              indicatorColor: AppColors.primary,
              indicatorWeight: 3,
              labelColor: AppColors.textPrimary,
              unselectedLabelColor: AppColors.textMuted,
              labelStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
              dividerColor: AppColors.divider,
              tabs: const [Tab(text: "🚀 급등"), Tab(text: "📉 급락")],
            ),
            SizedBox(
              height: _isExpanded ? 600 : 350,
              child: TabBarView(controller: _tabController, children: [
                _buildStockList(widget.gainers, true),
                _buildStockList(widget.losers, false),
              ]),
            ),
            TextButton(
              onPressed: () => setState(() => _isExpanded = !_isExpanded),
              child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                Text(_isExpanded ? "접기" : "더보기", style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600)),
                Icon(_isExpanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded, color: AppColors.primary),
              ]),
            ),
          ]),
        ),
      ],
    );
  }

  Widget _buildStockList(List<Stock> stocks, bool isGainer) {
    if (stocks.isEmpty) return Center(child: Text("데이터 없음", style: TextStyle(color: AppColors.textMuted)));
    final display = stocks.sublist(0, _isExpanded ? stocks.length : (stocks.length > 5 ? 5 : stocks.length));
    final cc = isGainer ? AppColors.marketUp : AppColors.marketDown;

    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      itemCount: display.length,
      itemBuilder: (context, index) {
        final stock = display[index];
        return InkWell(
          onTap: () {
             Navigator.push(
               context,
               MaterialPageRoute(
                 builder: (_) => StockDetailScreen(ticker: stock.ticker, name: stock.name),
               ),
             );
          },
          onLongPress: () => _showAddStockDialog(context, stock.ticker, stock.name),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: BoxDecoration(border: Border(bottom: BorderSide(color: AppColors.divider))),
            child: Row(children: [
              Container(
                width: 28, height: 28, alignment: Alignment.center,
                decoration: BoxDecoration(color: cc.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                child: Text("${index + 1}", style: TextStyle(color: cc, fontSize: 13, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(width: 14),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(stock.ticker, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600, fontSize: 15)),
                const SizedBox(height: 2),
                Text(stock.name, style: TextStyle(color: AppColors.textMuted, fontSize: 12), overflow: TextOverflow.ellipsis),
              ])),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: cc.withOpacity(0.08), borderRadius: BorderRadius.circular(8)),
                child: Text("${isGainer ? '+' : ''}${(stock.changePercent ?? 0.0).toStringAsFixed(2)}%",
                  style: TextStyle(color: cc, fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            ]),
          ),
        );
      },
    );
  }

  void _showAddStockDialog(BuildContext context, String ticker, String name) {
    // Note: Since ApiService is not passed, we create a new instance or pass it. 
    // Assuming ApiService is stateless or singleton-ish enough for this simple action,
    // or we should pass it from parent. For safe implementation, let's create a new instance here 
    // strictly for this action or better, pass it. 
    // However, looking at HomeScreen, `_apiService` is available in the parent state but not passed to this widget.
    // Instead of refactoring the whole widget constructor, using a fresh ApiService instance here is acceptable 
    // given the architecture shown so far (ApiService seems to be instantiated in Widgets).
    
    // Check if we can access ApiService. 
    // HomeScreen has ApiService. This widget is in the same file but outside _HomeScreenState.
    // Let's instantiate ApiService locally.
    final apiService = ApiService(); 

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
                await apiService.addToWatchlist(ticker, name);
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("'$name' 추가 완료!")));
                }
              } catch (e) {
                if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("오류: $e")));
              }
            },
            child: Text("추가"),
          ),
        ],
      ),
    );
  }
}

class _GlobalMarketCard extends StatefulWidget {
  final Map<String, dynamic>? marketIndices;
  final String hotMarket;
  final Function(String) getChange;
  final Function(String) getColor;
  final Function(String) getHistory;
  final String selectedMarket;
  final Function(int) onTabChanged;

  const _GlobalMarketCard({
    required this.marketIndices, 
    required this.hotMarket,
    required this.getChange,
    required this.getColor,
    required this.getHistory,
    required this.selectedMarket,
    required this.onTabChanged,
  });

  @override
  State<_GlobalMarketCard> createState() => _GlobalMarketCardState();
}

class _GlobalMarketCardState extends State<_GlobalMarketCard> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final List<String> _tabs = ["US", "KR", "Coin"];

  @override
  void initState() {
    super.initState();
    int initialIndex = _tabs.indexOf(widget.selectedMarket);
    if (initialIndex == -1) initialIndex = 0;
    _tabController = TabController(length: 3, vsync: this, initialIndex: initialIndex);
    
    // Optional: Add listener if we want to support swiping updates
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging && _tabController.index != _tabs.indexOf(widget.selectedMarket)) {
         widget.onTabChanged(_tabController.index);
      }
    });
  }

  @override
  void didUpdateWidget(_GlobalMarketCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedMarket != widget.selectedMarket) {
      int newIndex = _tabs.indexOf(widget.selectedMarket);
      if (newIndex != -1 && newIndex != _tabController.index) {
        _tabController.animateTo(newIndex);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return NeonGlassCard(
      glowColor: AppColors.primary,
      padding: const EdgeInsets.all(0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: Row(
              children: [
                Icon(Icons.public, color: AppColors.accentOrange, size: 20),
                const SizedBox(width: 6),
                Text(
                  '글로벌 시장 브리핑',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
                ),
              ],
            ),
          ),
          
          TabBar(
            controller: _tabController,
            labelColor: AppColors.textPrimary,
            unselectedLabelColor: AppColors.textMuted,
            indicatorColor: AppColors.accentOrange,
            dividerColor: AppColors.divider,
            labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            onTap: (index) {
                widget.onTabChanged(index);
            },
            tabs: _tabs.map((tab) {
              bool isHot = tab == widget.hotMarket;
              return Tab(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(tab == "US" ? "🇺🇸 미장" : tab == "KR" ? "🇰🇷 국장" : "🪙 코인"),
                    if (isHot) ...[
                      const SizedBox(width: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(color: AppColors.danger, borderRadius: BorderRadius.circular(4)),
                        child: const Text("HOT", style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
                      )
                    ]
                  ],
                ),
              );
            }).toList(),
          ),

          SizedBox(
            height: 140,
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildMarketList(["S&P 500", "Nasdaq", "Dow Jones"]),
                _buildMarketList(["KOSPI", "KOSDAQ"]),
                _buildMarketList(["Bitcoin", "Ethereum"]),
              ],
            ),
          ),

          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary.withOpacity(0.5),
              borderRadius: const BorderRadius.vertical(bottom: Radius.circular(16)),
            ),
            child: Text(
              "※ 제공된 데이터는 야후 파이낸스 기반으로 약 15분 지연될 수 있으며, 투자 참고용입니다.",
              style: TextStyle(color: AppColors.textMuted.withOpacity(0.7), fontSize: 10),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMarketList(List<String> tickers) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: tickers.map((ticker) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _buildIndexRow(ticker),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildIndexRow(String name) {
    // Robust checking using passed widget.marketIndices
    final data = widget.marketIndices?[name];
    
    // If data is missing (loading or error), show placeholder
    if (data == null) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SizedBox(width: 70, child: Text(name, style: TextStyle(color: AppColors.textPrimary, fontSize: 13, fontWeight: FontWeight.w600))),
          Text("-", style: TextStyle(color: AppColors.textMuted)),
          Text("-", style: TextStyle(color: AppColors.textMuted)),
        ],
      );
    }
    
    // Extract data safely
    final price = data['regularMarketPrice'];
    final change = data['regularMarketChangePercent'];
    
    // Fallback if individual fields are missing
    if (price == null || change == null) {
       return Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SizedBox(width: 70, child: Text(name, style: TextStyle(color: AppColors.textPrimary, fontSize: 13, fontWeight: FontWeight.w600))),
          Text("Data Error", style: TextStyle(color: AppColors.danger, fontSize: 10)),
        ],
      );
    }

    // Convert to proper types
    final double changeVal = (change is num) ? change.toDouble() : 0.0;
    final bool isPos = changeVal >= 0;
    final Color color = isPos ? AppColors.marketUp : AppColors.marketDown;
    
    // Chart data (mock logic or from history if available)
    final List<double> history = [0.0, 0.0]; 
    if (widget.getHistory(name).isNotEmpty) {
       // Try-catch for history mapping
       try {
         history.clear();
         history.addAll((widget.getHistory(name) as List<dynamic>).map((e) => (e as num).toDouble()));
       } catch(e) {
         history.add(0.0);
         history.add(0.0);
       }
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        SizedBox(width: 70, child: Text(name, style: TextStyle(color: AppColors.textPrimary, fontSize: 13, fontWeight: FontWeight.w600))),
        SizedBox(
          width: 50, height: 16, 
          child: Sparkline(
            data: history, 
            lineColor: color, 
            lineWidth: 2.0
          )
        ),
        Text(
          "${isPos ? '+' : ''}${changeVal.toStringAsFixed(2)}%", 
          style: TextStyle(color: color, fontSize: 13, fontWeight: FontWeight.bold)
        ),
      ],
    );
  }
}

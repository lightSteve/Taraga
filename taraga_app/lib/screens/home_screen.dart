import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import '../services/api_service.dart';
import '../models/theme.dart';
import '../models/stock.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import 'package:chart_sparkline/chart_sparkline.dart';
import 'theme_detail_screen.dart';

/// Home screen displaying daily briefing and theme recommendations
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

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final mode = await _apiService.getAppMode();
      final themes = await _apiService.getThemes();
      final matchesData = await _apiService.getPersonalMatches('test_user_uuid');
      final movers = await _apiService.getUSMarketMovers();
      final indices = await _apiService.getMarketIndices();

      setState(() {
        _appMode = mode;
        _themes = themes;
        _personalMatches = matchesData['personal_matches'] ?? [];
        _gainers = movers['gainers'] ?? [];
        _losers = movers['losers'] ?? [];
        _marketIndices = indices;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E27),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1A1F3A),
        elevation: 0,
        title: Row(
          children: [
            const Text(
              '🌉 ',
              style: TextStyle(fontSize: 24),
            ),
            const Text(
              'Taraga',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Text(
                '따라가',
                style: TextStyle(
                  color: Colors.blue,
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined, color: Colors.white),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('알림 기능 준비 중입니다.')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.blue))
          : _errorMessage != null
             ? _buildErrorView()
             : RefreshIndicator(
                  onRefresh: _loadData,
                  color: Colors.blue,
                  child: SingleChildScrollView(
                    physics: const AlwaysScrollableScrollPhysics(),
                    child: Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (_marketIndices != null) _buildMarketWeatherCard(),
                          const SizedBox(height: 16),
                          // Daily Briefing Card
                          _buildBriefingCard(),
                          const SizedBox(height: 24),
                          
                          // Personal Matches Section
                          if (_personalMatches.isNotEmpty)
                             ...[
                               _buildPersonalMatchesSection(),
                               const SizedBox(height: 24),
                             ],
                          const SizedBox(height: 24),

                          // NEW: Burger vs WallStreet Widget
                          _buildBurgerVsWallStreet(),
                          const SizedBox(height: 24),

                          // Theme Recommendations Section
                          _buildThemesSection(),
                          const SizedBox(height: 24),
                          
                          // Market Movers Widget
                          MarketMoversWidget(gainers: _gainers, losers: _losers),
                          const SizedBox(height: 24),
                        ],
                      ),
                    ),
                  ),
                ),
    );
  }


  Widget _buildBriefingCard() {
    // Helper to get change string
    String getChange(String ticker) {
      if (_marketIndices == null || !_marketIndices!.containsKey(ticker)) return "0.0%";
      double val = _marketIndices![ticker]['change_percent'] ?? 0.0;
      return "${val >= 0 ? '+' : ''}${val.toStringAsFixed(2)}%";
    }
    
    // Helper to decide color
    Color getColor(String ticker) {
       if (_marketIndices == null || !_marketIndices!.containsKey(ticker)) return Colors.grey;
       double val = _marketIndices![ticker]['change_percent'] ?? 0.0;
       return val >= 0 ? Colors.redAccent : Colors.blueAccent;
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16), // Reduced padding
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2C), // Darker card background
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
        const Text(
          '☀ 오늘의 시황 브리핑', // Translated title
          style: TextStyle(
            color: Colors.white70,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
          const SizedBox(height: 16),
          Row(
            children: [
              // 1. Radial Gauge (Fear/Greed)
              SizedBox(
                width: 120,
                height: 120,
                child: SfRadialGauge(
                  axes: <RadialAxis>[
                    RadialAxis(
                      minimum: 0,
                      maximum: 100,
                      showLabels: false,
                      showTicks: false,
                      axisLineStyle: const AxisLineStyle(
                        thickness: 0.2,
                        cornerStyle: CornerStyle.bothCurve,
                        color: Color.fromARGB(30, 0, 169, 181),
                        thicknessUnit: GaugeSizeUnit.factor,
                      ),
                      pointers: const <GaugePointer>[
                        RangePointer(
                          value: 75, // Mock value for "Greed"
                          cornerStyle: CornerStyle.bothCurve,
                          width: 0.2,
                          sizeUnit: GaugeSizeUnit.factor,
                          color: Colors.orangeAccent,
                        )
                      ],
                      annotations: const <GaugeAnnotation>[
                        GaugeAnnotation(
                          positionFactor: 0.1,
                          angle: 90,
                          widget: Text(
                            '75\n탐욕', // Translated "Greed"
                            textAlign: TextAlign.center,
                            style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white),
                          ),
                        )
                      ],
                    )
                  ],
                ),
              ),
              const SizedBox(width: 16),
              // 2. Index Trends with Sparklines
              Expanded(
                child: Column(
                  children: [
                    _buildIndexRow("S&P 500", getChange("^GSPC"), [10, 12, 11, 14, 13, 15, 16], getColor("^GSPC")),
                    const SizedBox(height: 12),
                    _buildIndexRow("Nasdaq", getChange("^IXIC"), [10, 11, 13, 14, 16, 18, 19], getColor("^IXIC")),
                    const SizedBox(height: 12),
                    _buildIndexRow("Dow", getChange("^DJI"), [15, 14, 13, 12, 13, 12, 11], getColor("^DJI")),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildIndexRow(String name, String change, List<double> data, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        SizedBox(
          width: 60,
          child: Text(name, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
        ),
        SizedBox(
          width: 40,
          height: 15,
          child: Sparkline(
            data: data,
            lineColor: color,
            lineWidth: 2.0,
          ),
        ),
        Text(change, style: TextStyle(color: color, fontSize: 13, fontWeight: FontWeight.bold)),
      ],
    );
  }

  Widget _buildThemesSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              '🔥 지금 뜨는 테마', // Translated title
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              '${_themes.length} 테마', // Translated "themes"
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 14,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.6,
          ),
          itemCount: _themes.length,
          itemBuilder: (context, index) {
            final theme = _themes[index];
            // Mock impact score for gradient intensity (0.3 ~ 0.8)
            final double opacity = 0.3 + (index % 3) * 0.2; 
            return _buildThemeGridCard(theme, opacity);
          },
        ),
      ],
    );
  }

  Widget _buildThemeGridCard(MarketTheme theme, double opacity) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ThemeDetailScreen(theme: theme),
            ),
          );
        },
        child: Container(
          decoration: BoxDecoration(
            color: Colors.redAccent.withOpacity(opacity), // Heatmap effect
            borderRadius: BorderRadius.circular(16),
          ),
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                   const Icon(Icons.local_fire_department, color: Colors.white, size: 20),
                   Text("+${(opacity * 5).toStringAsFixed(1)}%", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    theme.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    theme.keywords.first,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.8),
                      fontSize: 12,
                    ),
                  ),
                ],
              )
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
        const Text(
          '🎯 내 종목 분석', // Translated title
          style: TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ..._personalMatches.map((group) {
          return _buildGroupedMatchCard(group);
        }).toList(),
      ],
    );
  }

  Widget _buildGroupedMatchCard(Map<String, dynamic> group) {
    bool isPositive = (group['us_change_percent'] ?? 0) >= 0;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF252538), // Card Background
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                   children: [
                     const Icon(Icons.public, color: Colors.blueAccent, size: 20),
                     const SizedBox(width: 8),
                     Text(
                       group['theme_name'],
                       style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                     ),
                   ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: isPositive ? Colors.redAccent.withOpacity(0.2) : Colors.blueAccent.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${isPositive ? '+' : ''}${group['us_change_percent']}%',
                    style: TextStyle(
                      color: isPositive ? Colors.redAccent : Colors.blueAccent,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Reason Divider
          Divider(color: Colors.white.withOpacity(0.1), height: 1),
          Container(
             width: double.infinity,
             padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
             color: Colors.white.withOpacity(0.02),
             child: Text(
               "원인: ${group['reason']}",
               style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
             ),
          ),
          Divider(color: Colors.white.withOpacity(0.1), height: 1),

          // Body: Stock List
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: (group['my_stocks'] as List).length,
            separatorBuilder: (_, __) => Divider(color: Colors.white.withOpacity(0.05), height: 1),
            itemBuilder: (context, index) {
              final stock = group['my_stocks'][index];
              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 4, height: 4,
                          decoration: const BoxDecoration(color: Colors.redAccent, shape: BoxShape.circle),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          stock['name'],
                          style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w500),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          stock['ticker'],
                          style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 12),
                        ),
                      ],
                    ),
                    Row(
                       children: [
                          Icon(Icons.trending_up, color: Colors.redAccent, size: 18),
                          const SizedBox(width: 4),
                          Text("상승 예상", style: TextStyle(color: Colors.redAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                       ],
                    )
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // --- Burger (Retail) vs WallStreet (Institutional) Widget ---
  Widget _buildBurgerVsWallStreet() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              "🍔 버거형 vs 👔 월가 (핫 트렌드)",
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          _BurgerVsWallStreetSlider(apiService: _apiService),
        ],
      ),
    );
  }
}

// Separate stateful widget for auto-scrolling PageView
class _BurgerVsWallStreetSlider extends StatefulWidget {
  final ApiService apiService;

  const _BurgerVsWallStreetSlider({required this.apiService});

  @override
  State<_BurgerVsWallStreetSlider> createState() => _BurgerVsWallStreetSliderState();
}

class _BurgerVsWallStreetSliderState extends State<_BurgerVsWallStreetSlider> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  Timer? _autoScrollTimer;
  
  // Cache data to prevent re-loading
  List<dynamic>? _retailPicksData;
  List<dynamic>? _institutionalPicksData;
  bool _isLoadingRetail = true;
  bool _isLoadingInstitutional = true;

  @override
  void initState() {
    super.initState();
    _startAutoScroll();
    _loadData();
  }

  Future<void> _loadData() async {
    // Fetch both datasets once
    final retailFuture = widget.apiService.getRetailPicks();
    final institutionalFuture = widget.apiService.getInstitutionalPicks();

    retailFuture.then((data) {
      if (mounted) {
        setState(() {
          _retailPicksData = data;
          _isLoadingRetail = false;
        });
      }
    }).catchError((error) {
      if (mounted) {
        setState(() {
          _retailPicksData = [];
          _isLoadingRetail = false;
        });
      }
    });

    institutionalFuture.then((data) {
      if (mounted) {
        setState(() {
          _institutionalPicksData = data;
          _isLoadingInstitutional = false;
        });
      }
    }).catchError((error) {
      if (mounted) {
        setState(() {
          _institutionalPicksData = [];
          _isLoadingInstitutional = false;
        });
      }
    });
  }

  @override
  void dispose() {
    _autoScrollTimer?.cancel();
    _pageController.dispose();
    super.dispose();
  }

  void _startAutoScroll() {
    _autoScrollTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (_pageController.hasClients) {
        final nextPage = (_currentPage + 1) % 2; // 0 or 1
        _pageController.animateToPage(
          nextPage,
          duration: const Duration(milliseconds: 500),
          curve: Curves.easeInOut,
        );
      }
    });
  }

  void _resetTimer() {
    _autoScrollTimer?.cancel();
    _startAutoScroll();
  }

  void _goToPage(int page) {
    _resetTimer();
    _pageController.animateToPage(
      page,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Stack(
          children: [
            SizedBox(
              height: 280,
              child: PageView(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                  _resetTimer(); // Reset timer when user swipes
                },
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: _buildTrendCard(
                      title: "🍔 버거형들의 원픽",
                      subtitle: "커뮤니티(WSB) 급등 언급",
                      icon: "🍔",
                      color: Colors.orangeAccent,
                      items: _retailPicksData,
                      isLoading: _isLoadingRetail,
                      isRetail: true,
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: _buildTrendCard(
                      title: "💎 기관 강력 매수",
                      subtitle: "애널리스트 등급 상향",
                      icon: "👔",
                      color: Colors.blueAccent,
                      items: _institutionalPicksData,
                      isLoading: _isLoadingInstitutional,
                      isRetail: false,
                    ),
                  ),
                ],
              ),
            ),
            // Left Arrow
            if (_currentPage > 0)
              Positioned(
                left: 0,
                top: 0,
                bottom: 0,
                child: Center(
                  child: Container(
                    margin: const EdgeInsets.only(left: 8),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.5),
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.chevron_left, color: Colors.white, size: 28),
                      onPressed: () => _goToPage(_currentPage - 1),
                    ),
                  ),
                ),
              ),
            // Right Arrow
            if (_currentPage < 1)
              Positioned(
                right: 0,
                top: 0,
                bottom: 0,
                child: Center(
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.5),
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.chevron_right, color: Colors.white, size: 28),
                      onPressed: () => _goToPage(_currentPage + 1),
                    ),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 12),
        // Page Indicators
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(2, (index) {
            return GestureDetector(
              onTap: () => _goToPage(index),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                margin: const EdgeInsets.symmetric(horizontal: 4),
                width: _currentPage == index ? 24 : 8,
                height: 8,
                decoration: BoxDecoration(
                  color: _currentPage == index
                      ? (index == 0 ? Colors.orangeAccent : Colors.blueAccent)
                      : Colors.grey[700],
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
    required String title,
    required String subtitle,
    required String icon,
    required Color color,
    required List<dynamic>? items,
    required bool isLoading,
    required bool isRetail,
  }) {
    return InkWell(
      onTap: () {
        if (items != null && items.isNotEmpty) {
          _showTrendDetailsDialog(
            context: context,
            title: title,
            subtitle: subtitle,
            icon: icon,
            color: color,
            items: items,
            isRetail: isRetail,
          );
        }
      },
      borderRadius: BorderRadius.circular(20),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E2E),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.4), width: 2),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.2),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(icon, style: const TextStyle(fontSize: 32)),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        subtitle,
                        style: TextStyle(color: Colors.grey[400], fontSize: 14),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                Icon(Icons.touch_app, color: color.withOpacity(0.6), size: 20),
              ],
            ),
            const Divider(color: Colors.white10, height: 24, thickness: 1),
            SizedBox(
              height: 160,
              child: isLoading
                  ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
                  : (items == null || items.isEmpty)
                      ? Center(
                          child: Text(
                            "데이터 로딩 중...",
                            style: TextStyle(color: Colors.grey[600], fontSize: 14),
                          ),
                        )
                      : ListView.builder(
                          shrinkWrap: true,
                          physics: const NeverScrollableScrollPhysics(),
                          padding: EdgeInsets.zero,
                          itemCount: items.take(3).length,
                          itemBuilder: (context, index) {
                            final item = items[index];
                            final changePercent = item['change_percent'] ?? 0.0;
                            final isETF = item['type'] == 'ETF';
                            
                            // Weather emoji based on price change
                            String weatherEmoji = '☀️'; // Sunny (positive)
                            Color changeColor = Colors.green;
                            if (changePercent > 2) {
                              weatherEmoji = '🔥'; // Hot (strong positive)
                            } else if (changePercent > 0) {
                              weatherEmoji = '☀️'; // Sunny (mild positive)
                            } else if (changePercent > -2) {
                              weatherEmoji = '☁️'; // Cloudy (mild negative)
                              changeColor = Colors.grey;
                            } else {
                              weatherEmoji = '🌧️'; // Rainy (strong negative)
                              changeColor = Colors.red;
                            }
                            
                            return Padding(
                              padding: EdgeInsets.only(bottom: index < 2 ? 14.0 : 0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  Expanded(
                                    flex: 3,
                                    child: Row(
                                      children: [
                                        Column(
                                          children: [
                                            Container(
                                              constraints: const BoxConstraints(minWidth: 50, maxWidth: 65),
                                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                                              decoration: BoxDecoration(
                                                color: color.withOpacity(0.2),
                                                borderRadius: BorderRadius.circular(8),
                                              ),
                                              child: Text(
                                                item['ticker'] ?? '',
                                                style: TextStyle(
                                                  color: color,
                                                  fontWeight: FontWeight.bold,
                                                  fontSize: 14,
                                                ),
                                                textAlign: TextAlign.center,
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                            if (isETF)
                                              Container(
                                                margin: const EdgeInsets.only(top: 2),
                                                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                                                decoration: BoxDecoration(
                                                  color: Colors.purple.withOpacity(0.3),
                                                  borderRadius: BorderRadius.circular(4),
                                                  border: Border.all(color: Colors.purple.withOpacity(0.5), width: 0.5),
                                                ),
                                                child: const Text(
                                                  'ETF',
                                                  style: TextStyle(
                                                    color: Colors.purpleAccent,
                                                    fontSize:7,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ),
                                          ],
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                item['name'] ?? '',
                                                style: const TextStyle(
                                                  color: Colors.white,
                                                  fontSize: 15,
                                                  fontWeight: FontWeight.w600,
                                                ),
                                                maxLines: 1,
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                              Row(
                                                children: [
                                                  Text(
                                                    weatherEmoji,
                                                    style: const TextStyle(fontSize: 12),
                                                  ),
                                                  const SizedBox(width: 4),
                                                  Text(
                                                    '${changePercent > 0 ? '+' : ''}${changePercent.toStringAsFixed(1)}%',
                                                    style: TextStyle(
                                                      color: changeColor,
                                                      fontSize: 11,
                                                      fontWeight: FontWeight.w600,
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 8),
                                  Flexible(
                                    flex: 2,
                                    child: Text(
                                      isRetail
                                          ? (item['mentions'] ?? '')
                                          : (item['rating'] ?? '').replaceAll('Upgrade to ', ''),
                                      style: TextStyle(
                                        color: Colors.grey[400],
                                        fontSize: 11,
                                      ),
                                      textAlign: TextAlign.right,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            );
                          },
                        ),
            )
          ],
        ),
      ),
    );
  }

  void _showTrendDetailsDialog({
    required BuildContext context,
    required String title,
    required String subtitle,
    required String icon,
    required Color color,
    required List<dynamic> items,
    required bool isRetail,
  }) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: const Color(0xFF1A1A2E),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 500, maxHeight: 600),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(icon, style: const TextStyle(fontSize: 32)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          subtitle,
                          style: TextStyle(color: Colors.grey[400], fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close, color: Colors.white),
                  ),
                ],
              ),
              const Divider(color: Colors.white10, height: 32),
              Flexible(
                child: ListView.builder(
                  shrinkWrap: true,
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: const Color(0xFF252538),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: color.withOpacity(0.2)),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: color.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              item['ticker'] ?? '',
                              style: TextStyle(
                                color: color,
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  item['name'] ?? '',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 15,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  isRetail
                                      ? '📈 ${item['mentions'] ?? ''}'
                                      : '💼 ${item['rating'] ?? ''}',
                                  style: TextStyle(
                                    color: Colors.grey[400],
                                    fontSize: 13,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
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

// === Back to _HomeScreenState methods ===
extension _HomeScreenMethods on _HomeScreenState {
  Widget _buildMarketWeatherCard() {
    // 1. Get S&P 500 Change
    // yfinance returns keys: ^GSPC, ^IXIC, ^DJI
    // Or sometimes mapped names if backend handled it. 
    // Assuming backend polygon_service.py returns dict with keys matching backend.
    
    // Let's check keys carefully. Our backend polygon_service.get_market_indices structure:
    // { "^GSPC": { "name": "S&P 500", "change_percent": X.X, ... }, ... }
    
    double changePercent = 0.0;
    if (_marketIndices != null && _marketIndices!.containsKey('^GSPC')) {
        changePercent = _marketIndices!['^GSPC']['change_percent'] ?? 0.0;
    }

    // 2. Determine Weather Status
    String emoji = "☁️";
    String title = "Market is Cloudy";
    String message = "변동성이 적은 흐린 장세";
    List<Color> gradientColors = [Colors.grey.shade700, Colors.grey.shade900];

    if (changePercent >= 1.0) {
      emoji = "🔥";
      title = "Fires (불장)";
      message = "뜨거운 불장입니다! 테마주에 주목하세요.";
      gradientColors = [const Color(0xFFE53935), const Color(0xFF8E0000)];
    } else if (changePercent >= 0.0) {
      emoji = "☀";
      title = "Sunny (맑음)";
      message = "시장이 맑습니다. 완만한 상승세.";
      gradientColors = [const Color(0xFFFFA726), const Color(0xFFF57C00)];
    } else if (changePercent >= -1.0) {
      emoji = "☁️";
      title = "Cloudy (흐림)";
      message = "다소 흐린 장세입니다. 관망이 필요해요.";
      gradientColors = [const Color(0xFF78909C), const Color(0xFF37474F)];
    } else {
      emoji = "☔";
      title = "Rain (비)";
      message = "비가 내립니다. 리스크 관리가 필수입니다.";
      gradientColors = [const Color(0xFF5C6BC0), const Color(0xFF283593)];
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: gradientColors,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: gradientColors.last.withOpacity(0.5),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: Stack(
        children: [
          // Background Pattern (Optional subtle detail)
          Positioned(
            right: -20,
            top: -20,
            child: Icon(Icons.cloud, size: 150, color: Colors.white.withOpacity(0.1)),
          ),
          
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                // 3D Emoji
                Text(
                  emoji,
                  style: const TextStyle(fontSize: 48),
                ),
                const SizedBox(width: 16),
                
                // Weather Info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        message,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 13,
                        ),
                        maxLines: 2,
                      ),
                    ],
                  ),
                ),

                // Index Value
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      const Text("S&P 500", style: TextStyle(color: Colors.white70, fontSize: 10)),
                      Text(
                        "${changePercent >= 0 ? '+' : ''}${changePercent.toStringAsFixed(2)}%",
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                )
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 64),
            const SizedBox(height: 16),
            Text('데이터 로딩 오류', style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 18)),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(_errorMessage!, textAlign: TextAlign.center, style: TextStyle(color: Colors.white.withOpacity(0.5))),
            ),
            ElevatedButton(
              onPressed: _loadData,
              child: const Text('재시도'),
            )
          ],
        ),
    );
  }
}
class MarketMoversWidget extends StatefulWidget {
  final List<Stock> gainers;
  final List<Stock> losers;

  const MarketMoversWidget({super.key, required this.gainers, required this.losers});

  @override
  State<MarketMoversWidget> createState() => _MarketMoversWidgetState();
}

class _MarketMoversWidgetState extends State<MarketMoversWidget> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isExpanded = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white54,
          labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          tabs: const [
            Tab(text: "🚀 급등 (Gainers)"),
            Tab(text: "📉 급락 (Losers)"),
          ],
        ),
        SizedBox(
          height: _isExpanded ? 600 : 350, // Dynamic height
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildStockList(widget.gainers, true),
              _buildStockList(widget.losers, false),
            ],
          ),
        ),
        TextButton(
          onPressed: () {
            setState(() {
              _isExpanded = !_isExpanded;
            });
          },
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(_isExpanded ? "접기 (Show Less)" : "더보기 (View More)", style: const TextStyle(color: Colors.white70)),
              Icon(_isExpanded ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down, color: Colors.white70),
            ],
          ),
        )
      ],
    );
  }

  Widget _buildStockList(List<Stock> stocks, bool isGainer) {
    if (stocks.isEmpty) return const Center(child: Text("데이터 없음", style: TextStyle(color: Colors.white54)));

    final displayCount = _isExpanded ? stocks.length : (stocks.length > 5 ? 5 : stocks.length);
    final displayList = stocks.sublist(0, displayCount);

    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      itemCount: displayList.length,
      itemBuilder: (context, index) {
        final stock = displayList[index];
        final changeColor = isGainer ? Colors.redAccent : Colors.blueAccent;
        
        return Container(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          decoration: BoxDecoration(
            border: Border(bottom: BorderSide(color: Colors.white.withOpacity(0.05))),
          ),
          child: Row(
            children: [
              // Rank
              Text(
                "${index + 1}",
                style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 14, fontWeight: FontWeight.bold),
              ),
              const SizedBox(width: 16),
              
              // Ticker & Name
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(stock.ticker, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 2),
                    Text(stock.name, style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12), overflow: TextOverflow.ellipsis),
                  ],
                ),
              ),

              // Change %
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: changeColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  "${isGainer ? '+' : ''}${(stock.changePercent ?? 0.0).toStringAsFixed(2)}%",
                  style: TextStyle(color: changeColor, fontWeight: FontWeight.bold, fontSize: 14),
                ),
              )
            ],
          ),
        );
      },
    );
  }
}
 

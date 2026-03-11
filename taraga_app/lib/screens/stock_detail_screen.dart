import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'dart:math';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class StockDetailScreen extends StatefulWidget {
  final String ticker;
  final String name;

  const StockDetailScreen({super.key, required this.ticker, required this.name});

  @override
  State<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends State<StockDetailScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  Map<String, dynamic>? _stockData;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() { _isLoading = true; _errorMessage = null; });
    try {
      final data = await _apiService.getStockDetail(widget.ticker);
      if (data.isEmpty) {
        throw Exception("데이터를 불러올 수 없습니다.");
      }
      setState(() {
        _stockData = data;
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
      backgroundColor: AppColors.bgPrimary,
      appBar: AppBar(
        backgroundColor: AppColors.bgPrimary,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new_rounded, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(widget.name, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: AppColors.primary))
          : _errorMessage != null
              ? Center(child: Text(_errorMessage!, style: TextStyle(color: AppColors.danger)))
              : SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildHeader(),
                      const SizedBox(height: 24),
                      _buildChart(),
                      const SizedBox(height: 24),
                      _buildStatsGrid(),
                      const SizedBox(height: 24),
                      _buildSummarySection(),
                      const SizedBox(height: 40),
                    ],
                  ),
                ),
    );
  }

  Widget _buildHeader() {
    final price = _stockData!['price'] ?? 0.0;
    final change = _stockData!['change_percent'] ?? 0.0;
    final currency = _stockData!['currency'] ?? 'USD';
    final isPositive = change >= 0;
    final color = isPositive ? AppColors.success : AppColors.danger;

    String priceStr = currency == 'KRW' 
        ? "₩${price.toStringAsFixed(0).replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]},')}"
        : "\$${price.toStringAsFixed(2)}";

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(widget.ticker, style: TextStyle(color: AppColors.textMuted, fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(priceStr, style: TextStyle(color: AppColors.textPrimary, fontSize: 36, fontWeight: FontWeight.w800, height: 1.0)),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              margin: const EdgeInsets.only(bottom: 6),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                   Text(isPositive ? "▲" : "▼", style: TextStyle(color: color, fontSize: 12)),
                   const SizedBox(width: 4),
                   Text("${change.toStringAsFixed(2)}%", style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildChart() {
    List<dynamic> history = _stockData!['history'] ?? [];
    if (history.isEmpty) {
      return Container(
        height: 250,
        alignment: Alignment.center,
        decoration: AppDecorations.neonCard(),
        child: Text("차트 데이터 없음", style: TextStyle(color: AppColors.textMuted)),
      );
    }

    // Prepare spots
    List<FlSpot> spots = [];
    double minPrice = double.infinity;
    double maxPrice = double.negativeInfinity;

    for (int i = 0; i < history.length; i++) {
      double close = (history[i]['close'] as num).toDouble();
      if (close < minPrice) minPrice = close;
      if (close > maxPrice) maxPrice = close;
      spots.append(FlSpot(i.toDouble(), close));
    }

    // Padding for chart Y-axis
    double yRange = maxPrice - minPrice;
    minPrice -= yRange * 0.1;
    maxPrice += yRange * 0.1;

    final change = _stockData!['change_percent'] ?? 0.0;
    final lineColor = change >= 0 ? AppColors.success : AppColors.danger;

    return Container(
      height: 300,
      padding: const EdgeInsets.fromLTRB(16, 24, 24, 10),
      decoration: AppDecorations.neonCard(),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: (history.length - 1).toDouble(),
          minY: minPrice,
          maxY: maxPrice,
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: lineColor,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: lineColor.withOpacity(0.1),
                gradient: LinearGradient(
                  colors: [lineColor.withOpacity(0.2), lineColor.withOpacity(0.0)],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              getTooltipColor: (touchedSpot) => AppColors.bgSecondary,
              getTooltipItems: (touchedSpots) {
                return touchedSpots.map((spot) {
                  return LineTooltipItem(
                    spot.y.toStringAsFixed(2),
                    TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold),
                  );
                }).toList();
              },
            ),
            handleBuiltInTouches: true,
          ),
        ),
      ),
    );
  }

  Widget _buildStatsGrid() {
    final marketCap = _formatNumber(_stockData!['market_cap']);
    final volume = _formatNumber(_stockData!['volume']);
    final pe = _stockData!['pe_ratio'] != null ? _stockData!['pe_ratio'].toString() : '-';
    final sector = _stockData!['sector'] ?? 'Unknown';

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      childAspectRatio: 2.5,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      children: [
        _buildStatItem("시가총액", marketCap),
        _buildStatItem("거래량", volume),
        _buildStatItem("PER", pe),
        _buildStatItem("섹터", sector),
      ],
    );
  }

  Widget _buildStatItem(String label, String value) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label, style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 15), maxLines: 1, overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }

  Widget _buildSummarySection() {
    final description = _stockData!['description'] ?? "설명이 없습니다.";
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("기업 개요", style: TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.w700)),
        const SizedBox(height: 12),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(16),
          decoration: AppDecorations.neonCard(),
          child: Text(
            description,
            style: TextStyle(color: AppColors.textSecondary, height: 1.5, fontSize: 14),
          ),
        ),
      ],
    );
  }

  String _formatNumber(dynamic number) {
    if (number == null) return '-';
    if (number is! num) return number.toString();
    
    double numVal = number.toDouble();
    if (numVal >= 1e12) return "${(numVal / 1e12).toStringAsFixed(2)}T";
    if (numVal >= 1e9) return "${(numVal / 1e9).toStringAsFixed(2)}B";
    if (numVal >= 1e6) return "${(numVal / 1e6).toStringAsFixed(2)}M";
    return numVal.toStringAsFixed(0);
  }
}

extension ListAppend<T> on List<T> {
  void append(T item) => add(item);
}

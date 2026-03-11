import 'package:flutter/material.dart';
import '../models/theme.dart';
import '../models/stock.dart';
import '../models/value_chain.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

/// Theme detail screen showing Korean stocks for a selected theme
class ThemeDetailScreen extends StatefulWidget {
  final MarketTheme theme;

  const ThemeDetailScreen({
    super.key,
    required this.theme,
  });

  @override
  State<ThemeDetailScreen> createState() => _ThemeDetailScreenState();
}

class _ThemeDetailScreenState extends State<ThemeDetailScreen> {
  final ApiService _apiService = ApiService();
  List<Stock> _stocks = [];
  ValueChainResponse? _valueChain;
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadStocks();
  }

  Future<void> _loadStocks() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final stocks = await _apiService.getKoreanStocksByTheme(widget.theme.id);
      final valueChain = await _apiService.getValueChain(widget.theme.id);
      
      setState(() {
        _stocks = stocks;
        _valueChain = valueChain;
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
          icon: Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          widget.theme.name,
          style: TextStyle(
            color: AppColors.textPrimary,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: AppColors.textMuted),
            onPressed: _loadStocks,
          ),
        ],
      ),
      body: Column(
        children: [
          // Theme Info Header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: AppColors.blueGradient,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '관련 키워드',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: widget.theme.keywords.map((keyword) {
                    return Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        keyword,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
          
          if (!_isLoading && _valueChain != null)
            _buildValueChainMap(),

          // Stocks List
          Expanded(
            child: _isLoading
                ? Center(
                    child: CircularProgressIndicator(
                      color: AppColors.primary,
                    ),
                  )
                : _errorMessage != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.error_outline,
                              color: AppColors.danger,
                              size: 64,
                            ),
                            const SizedBox(height: 16),
                            Text(
                              '종목 데이터를 불러올 수 없습니다',
                              style: TextStyle(
                                color: AppColors.textSecondary,
                                fontSize: 18,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 32),
                              child: Text(
                                _errorMessage!,
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: AppColors.textMuted,
                                  fontSize: 14,
                                ),
                              ),
                            ),
                            const SizedBox(height: 24),
                            ElevatedButton(
                              onPressed: _loadStocks,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: AppColors.primary,
                                foregroundColor: Colors.white,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                              ),
                              child: const Text('재시도'),
                            ),
                          ],
                        ),
                      )
                    : _stocks.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.inbox_outlined,
                                  color: AppColors.textLight,
                                  size: 64,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  '이 테마에 해당하는 종목이 없습니다',
                                  style: TextStyle(
                                    color: AppColors.textMuted,
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                          )
                        : RefreshIndicator(
                            onRefresh: _loadStocks,
                            color: AppColors.primary,
                            child: ListView.builder(
                              padding: const EdgeInsets.all(16),
                              itemCount: _stocks.length,
                              itemBuilder: (context, index) {
                                final stock = _stocks[index];
                                return _buildStockCard(stock);
                              },
                            ),
                          ),
          ),
        ],
      ),
    );
  }

  Widget _buildStockCard(Stock stock) {
    final hasPrice = stock.currentPrice != null;
    final hasChange = stock.changePercent != null;
    final isPositive = hasChange && (stock.changePercent! > 0);
    final isNegative = hasChange && (stock.changePercent! < 0);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: AppDecorations.cleanCard(borderRadius: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      stock.name,
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      stock.ticker,
                      style: TextStyle(
                        color: AppColors.textMuted,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (hasPrice)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '₩${stock.currentPrice!.toStringAsFixed(0)}',
                      style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (hasChange)
                      Container(
                        margin: const EdgeInsets.only(top: 4),
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: isPositive ? AppColors.marketUp.withOpacity(0.1) : isNegative ? AppColors.marketDown.withOpacity(0.1) : AppColors.bgSecondary,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          '${isPositive ? '+' : ''}${stock.changePercent!.toStringAsFixed(2)}%',
                          style: TextStyle(
                            color: isPositive ? AppColors.marketUp : isNegative ? AppColors.marketDown : AppColors.textMuted,
                            fontSize: 12, fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                  ],
                ),
              const SizedBox(width: 12),
              Column(
                children: [
                  IconButton(
                    icon: Icon(Icons.add_circle_outline_rounded, color: AppColors.primary),
                    onPressed: () => _addToWatchlist(stock),
                    tooltip: "관심종목 추가",
                  ),
                ],
              ),
            ],
          ),
          if (stock.sector != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: AppColors.primaryLight,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                stock.sector!,
                style: TextStyle(
                  color: AppColors.primary,
                  fontSize: 11,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }


  Widget _buildValueChainMap() {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: AppDecorations.accentCard(accentColor: AppColors.accentPurple, borderRadius: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '🔗 밸류체인 맵',
            style: TextStyle(
              color: AppColors.textPrimary,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          if (_valueChain?.usDrivers.isNotEmpty == true)
            ..._valueChain!.usDrivers.entries.map((entry) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                   Container(
                     padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                     decoration: BoxDecoration(
                       color: AppColors.accentPurple.withOpacity(0.1),
                       borderRadius: BorderRadius.circular(8),
                     ),
                     child: Text(
                       '🇺🇸 ${entry.key} (Driver)',
                       style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold),
                     ),
                   ),
                   const SizedBox(height: 8),
                   Padding(
                     padding: const EdgeInsets.only(left: 16.0),
                     child: Container(
                       padding: const EdgeInsets.only(left: 16),
                       decoration: BoxDecoration(
                         border: Border(left: BorderSide(color: AppColors.accentPurple.withOpacity(0.3), width: 2)),
                       ),
                       child: Column(
                         children: entry.value.map((item) => Padding(
                           padding: const EdgeInsets.only(bottom: 8.0),
                           child: Row(
                             children: [
                               Icon(Icons.subdirectory_arrow_right, color: AppColors.textMuted, size: 16),
                               const SizedBox(width: 8),
                               Expanded(
                                 child: Column(
                                   crossAxisAlignment: CrossAxisAlignment.start,
                                   children: [
                                     Text(
                                       '🇰🇷 ${item.krStock}', 
                                       style: TextStyle(color: AppColors.textPrimary, fontSize: 14),
                                     ),
                                     Text(
                                       '${item.relation}: ${item.description}',
                                       style: TextStyle(color: AppColors.textMuted, fontSize: 12),
                                     ),
                                   ],
                                 ),
                               ),
                             ],
                           ),
                         )).toList(),
                       ),
                     ),
                   ),
                   const SizedBox(height: 16),
                ],
              );
            }).toList(),
        ],
      ),
    );
  }

  Future<void> _addToWatchlist(Stock stock) async {
    try {
      await _apiService.addToWatchlist(stock.ticker, stock.name);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('${stock.name} 관심종목 추가 완료')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('추가 실패: $e')),
        );
      }
    }
  }
}

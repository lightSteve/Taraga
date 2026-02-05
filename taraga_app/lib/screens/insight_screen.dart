import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../models/bridge_news.dart';

class InsightScreen extends StatefulWidget {
  const InsightScreen({super.key});

  @override
  State<InsightScreen> createState() => _InsightScreenState();
}

class _InsightScreenState extends State<InsightScreen> {
  final ApiService _apiService = ApiService();
  List<BridgeNews> _newsList = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadNews();
  }

  Future<void> _loadNews() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final news = await _apiService.getBridgeNews();
      setState(() {
        _newsList = news;
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
      appBar: AppBar(
        title: const Text('💡 Insight Bridge', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1A1F3A),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _loadNews,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.blue))
          : _errorMessage != null
              ? Center(child: Text('Error: $_errorMessage', style: const TextStyle(color: Colors.white)))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _newsList.length,
                  itemBuilder: (context, index) {
                    return _buildNewsCard(_newsList[index]);
                  },
                ),
    );
  }

  Widget _buildNewsCard(BridgeNews news) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: const Color(0xFF1E1E2C),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          // US Section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.blue.withOpacity(0.1),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text('🇺🇸', style: TextStyle(fontSize: 18)),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.blueAccent,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        news.usSource,
                        style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const Spacer(),
                    Text(
                      _formatDate(news.timestamp),
                      style: TextStyle(color: Colors.white.withOpacity(0.5), fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  news.usHeadline,
                  style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
          
          // Bridge Arrow
          SizedBox(
            height: 20,
            child: Stack(
              alignment: Alignment.center,
              children: [
                const Divider(height: 1, color: Colors.white10),
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E1E2C),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white10),
                  ),
                  child: const Icon(Icons.arrow_downward, color: Colors.amber, size: 16),
                ),
              ],
            ),
          ),

          // KR Section
          Container(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text('🇰🇷', style: TextStyle(fontSize: 18)),
                    const SizedBox(width: 8),
                    Text(
                      'Market Impact',
                      style: TextStyle(color: Colors.amber.shade400, fontSize: 14, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  news.krImpact,
                  style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14),
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: news.relatedStocks.map((stock) => _buildStockChip(stock)).toList(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStockChip(RelatedStock stock) {
    final isPositive = stock.change.contains('+');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFF2C2C3E),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isPositive ? Colors.red.withOpacity(0.5) : Colors.grey.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(stock.name, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500)),
          const SizedBox(width: 6),
          Text(
            stock.change,
            style: TextStyle(
              color: isPositive ? Colors.redAccent : Colors.grey,
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return "${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}";
  }
}

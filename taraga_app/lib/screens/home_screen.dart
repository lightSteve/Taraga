import 'package:flutter/material.dart';
import '../models/briefing.dart';
import '../models/recommended_theme.dart';
import '../services/api_service.dart';
import '../widgets/briefing_card.dart';
import '../widgets/theme_card.dart';
import 'theme_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  bool _isLoading = true;
  String? _errorMessage;
  Briefing? _briefing;
  List<RecommendedTheme> _recommendations = [];

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
      // Check API health first
      final isHealthy = await _apiService.checkHealth();
      if (!isHealthy) {
        throw Exception('Backend server is not responding. Please make sure the server is running at http://localhost:8000');
      }

      // Load briefing and recommendations in parallel
      final results = await Future.wait([
        _apiService.getTodayBriefing(),
        _apiService.getThemeRecommendations(),
      ]);

      setState(() {
        _briefing = results[0] as Briefing;
        _recommendations = results[1] as List<RecommendedTheme>;
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
        title: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Taraga 따라가'),
            Text(
              'Wall Street to Yeouido',
              style: TextStyle(fontSize: 12),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                'Error',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        children: [
          // Daily Briefing Section
          if (_briefing != null) BriefingCard(briefing: _briefing!),

          // Recommended Themes Section
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.recommend, color: Colors.orange),
                const SizedBox(width: 8),
                Text(
                  'Recommended Korean Themes',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ),

          if (_recommendations.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Center(
                child: Text('No recommendations available'),
              ),
            )
          else
            ..._recommendations.map((theme) {
              return ThemeCard(
                theme: theme,
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => ThemeDetailScreen(theme: theme),
                    ),
                  );
                },
              );
            }).toList(),

          const SizedBox(height: 16),
        ],
      ),
    );
  }
}

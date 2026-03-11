import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/theme.dart';
import '../models/stock.dart';
import '../models/briefing.dart';
import '../models/value_chain.dart';
import '../models/bridge_news.dart';
import 'user_service.dart';

/// API service for communicating with Taraga backend
class ApiService {
  // Base URL for the API
  // - Android emulator: http://10.0.2.2:8000/api/v1
  // - iOS simulator / macOS: http://localhost:8000/api/v1
  // - Real device: Replace with your server's LAN IP
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api/v1',
  );
  
  final UserService _userService = UserService();

  /// Fetch all available themes
  Future<List<MarketTheme>> getThemes() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/themes/list'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        // Explicitly decode as UTF-8 to handle Korean characters properly
        final String responseBody = utf8.decode(response.bodyBytes);
        final List<dynamic> jsonData = json.decode(responseBody);
        return jsonData.map((json) => MarketTheme.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load themes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching themes: $e');
    }
  }

  /// Fetch recommended themes for today
  Future<List<Map<String, dynamic>>> getRecommendedThemes() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/themes/recommendations'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final List<dynamic> jsonData = json.decode(responseBody);
        return jsonData.cast<Map<String, dynamic>>();
      } else {
        throw Exception(
            'Failed to load recommendations: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching recommendations: $e');
    }
  }

  /// Fetch Korean stocks for a specific theme
  Future<List<Stock>> getKoreanStocksByTheme(int themeId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/themes/$themeId/stocks'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final List<dynamic> jsonData = json.decode(responseBody);
        return jsonData.map((json) => Stock.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load stocks: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching stocks: $e');
    }
  }

  /// Fetch today's market briefing
  Future<Briefing> getTodayBriefing() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/briefing/today'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final jsonData = json.decode(responseBody);
        return Briefing.fromJson(jsonData);
      } else {
        throw Exception('Failed to load briefing: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching briefing: $e');
    }
  }

  /// Fetch US market top gainers & losers
  Future<Map<String, List<Stock>>> getUSMarketMovers() async {
    try {
      final gainersResponse = await http.get(Uri.parse('$baseUrl/market/us/top-gainers'));
      final losersResponse = await http.get(Uri.parse('$baseUrl/market/us/top-losers'));

      List<Stock> gainers = [];
      List<Stock> losers = [];

      if (gainersResponse.statusCode == 200) {
        final json = jsonDecode(gainersResponse.body);
        if (json['status'] == 'success') {
          gainers = (json['data'] as List).map((e) => Stock.fromJson(e)).toList();
        }
      }

      if (losersResponse.statusCode == 200) {
        final json = jsonDecode(losersResponse.body);
        if (json['status'] == 'success') {
          losers = (json['data'] as List).map((e) => Stock.fromJson(e)).toList();
        }
      }

      return {"gainers": gainers, "losers": losers};
    } catch (e) {
      print('Error fetching market movers: $e');
      return {"gainers": [], "losers": []};
    }
  }
  /// Fetch personal stock matches for a user
  Future<Map<String, dynamic>> getPersonalMatches() async {
    try {
      final userUuid = await _userService.getUserUuid();
      final response = await http.get(
        Uri.parse('$baseUrl/insight/personal-matches?user_uuid=$userUuid'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        return json.decode(responseBody);
      } else if (response.statusCode == 404) {
        // User not found or no matches yet
        return {"personal_matches": []};
      } else {
        throw Exception(
            'Failed to load personal matches: ${response.statusCode}');
      }
    } catch (e) {
      print('Error fetching personal matches: $e');
      return {"personal_matches": []};
    }
  }

  /// Fetch value chain data for a theme
  Future<ValueChainResponse> getValueChain(int themeId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/insight/value-chain?theme_id=$themeId'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        return ValueChainResponse.fromJson(json.decode(responseBody));
      } else {
        throw Exception('Failed to load value chain: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching value chain: $e');
    }
  }

  /// Fetch bridge news for Insight Tab
  Future<List<BridgeNews>> getBridgeNews() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/insight/news-bridge'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final Map<String, dynamic> data = json.decode(responseBody);
        final List<dynamic> newsList = data['news'] ?? [];
        return newsList.map((e) => BridgeNews.fromJson(e)).toList();
      } else {
        throw Exception('Failed to load bridge news: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching bridge news: $e');
    }
  }

  /// Watchlist APIs
  Future<List<dynamic>> getWatchlist() async {
    try {
      final userUuid = await _userService.getUserUuid();
      final response = await http.get(Uri.parse('$baseUrl/watchlist/$userUuid'));
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else if (response.statusCode == 404) {
        // Watchlist not found (empty) - return empty list instead of throwing error
        return [];
      } else {
        throw Exception('Failed to load watchlist: ${response.statusCode}');
      }
    } catch (e) {
      // Return empty list for any errors to prevent UI crashes
      print('Watchlist error (returning empty): $e');
      return [];
    }
  }

  Future<void> addToWatchlist(String ticker, String name) async {
    try {
      final userUuid = await _userService.getUserUuid();
      final response = await http.post(
        Uri.parse('$baseUrl/watchlist/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_uuid': userUuid,
          'ticker': ticker,
          'stock_name': name,
        }),
      );
      if (response.statusCode != 200) {
        throw Exception('Failed to add to watchlist: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error adding to watchlist: $e');
    }
  }

  Future<void> removeFromWatchlist(int itemId) async {
    try {
      final response = await http.delete(Uri.parse('$baseUrl/watchlist/$itemId'));
      if (response.statusCode != 200) {
        throw Exception('Failed to delete from watchlist: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error removing from watchlist: $e');
    }
  }

  /// Search Stocks (KR)
  Future<List<dynamic>> searchStock(String query) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/search?query=$query'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        return json.decode(responseBody);
      } else {
        throw Exception('Failed to search stocks: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error searching stocks: $e');
    }
  }

  /// Get Calendar Events
  Future<List<dynamic>> getCalendarEvents(int year, int month) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/calendar/events?year=$year&month=$month'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        return json['data'] ?? [];
      } else {
        throw Exception('Failed to load events: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error loading events: $e');
    }
  }

  /// Get App Mode (Time-based system status)
  Future<Map<String, dynamic>> getAppMode() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/system/mode'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        return json['data'] ?? {};
      } else {
        throw Exception('Failed to load system mode: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error loading system mode: $e');
    }
  }

  /// Get US Market Indices (Snapshot)
  Future<Map<String, dynamic>> getMarketIndices() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/us/snapshot'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        return json['data'] ?? {};
      } else {
        throw Exception('Failed to load indices: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error loading indices: $e');
    }
  }

  /// Get Retail (WSB/Community) Picks
  Future<List<dynamic>> getRetailPicks({String region = "US"}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/us/trends/retail?region=$region'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        return json['data'];
      } else {
        return [];
      }
    } catch (e) {
      print('Error loading retail picks: $e');
      return [];
    }
  }

  /// Get Detailed Stock Info (Price + History + Stats)
  Future<Map<String, dynamic>> getStockDetail(String ticker) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/stock/$ticker'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        if (json['status'] == 'success') {
           return json['data'];
        }
      }
      return {};
    } catch (e) {
      print('Error loading stock detail: $e');
      return {};
    }
  }

  /// Get Institutional (Whale/Foreign) Picks
  Future<List<dynamic>> getInstitutionalPicks({String region = "US"}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/us/trends/institutional?region=$region'),
        headers: {'Accept': 'application/json; charset=utf-8'},
      );

      if (response.statusCode == 200) {
        final String responseBody = utf8.decode(response.bodyBytes);
        final json = jsonDecode(responseBody);
        return json['data'];
      } else {
        return [];
      }
    } catch (e) {
      print('Error loading institutional picks: $e');
      return [];
    }
  }
}

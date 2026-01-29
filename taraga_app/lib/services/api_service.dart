import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/theme.dart';
import '../models/stock.dart';
import '../models/briefing.dart';

/// API service for communicating with Taraga backend
class ApiService {
  // Base URL for the API - change this to your actual server URL
  static const String baseUrl = 'http://localhost:8000/api/v1';

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

  /// Fetch US market top gainers
  Future<List<Stock>> getUSTopGainers() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/market/us/top-gainers'),
      );

      if (response.statusCode == 200) {
        final List<dynamic> jsonData = json.decode(response.body);
        return jsonData.map((json) => Stock.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load top gainers: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching top gainers: $e');
    }
  }
}

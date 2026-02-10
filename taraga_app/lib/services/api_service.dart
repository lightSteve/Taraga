import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/briefing.dart';
import '../models/recommended_theme.dart';
import '../models/theme.dart';

class ApiService {
  // Default to localhost, can be changed for production
  final String baseUrl;

  ApiService({this.baseUrl = 'http://localhost:8000'});

  // Get today's briefing
  Future<Briefing> getTodayBriefing() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/briefing/today'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Briefing.fromJson(data);
      } else if (response.statusCode == 404) {
        throw Exception('No briefing available for today. Please run daily analysis first.');
      } else {
        throw Exception('Failed to load briefing: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching briefing: $e');
    }
  }

  // Get theme recommendations
  Future<List<RecommendedTheme>> getThemeRecommendations() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/themes/recommendations'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => RecommendedTheme.fromJson(json)).toList();
      } else if (response.statusCode == 404) {
        throw Exception('No recommendations available for today. Please run daily analysis first.');
      } else {
        throw Exception('Failed to load recommendations: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching recommendations: $e');
    }
  }

  // Get all themes
  Future<List<Theme>> getAllThemes() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/themes/list'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => Theme.fromJson(json)).toList();
      } else {
        throw Exception('Failed to load themes: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching themes: $e');
    }
  }

  // Health check
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

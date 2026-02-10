class RecommendedTheme {
  final int themeId;
  final String themeName;
  final List<String> keywords;
  final String reason;
  final String? relatedUsStock;
  final int impactScore;
  final DateTime date;

  RecommendedTheme({
    required this.themeId,
    required this.themeName,
    required this.keywords,
    required this.reason,
    this.relatedUsStock,
    required this.impactScore,
    required this.date,
  });

  factory RecommendedTheme.fromJson(Map<String, dynamic> json) {
    return RecommendedTheme(
      themeId: json['theme_id'],
      themeName: json['theme_name'] ?? '',
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      reason: json['reason'] ?? '',
      relatedUsStock: json['related_us_stock'],
      impactScore: json['impact_score'] ?? 0,
      date: DateTime.parse(json['date']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'theme_id': themeId,
      'theme_name': themeName,
      'keywords': keywords,
      'reason': reason,
      'related_us_stock': relatedUsStock,
      'impact_score': impactScore,
      'date': date.toIso8601String(),
    };
  }
}

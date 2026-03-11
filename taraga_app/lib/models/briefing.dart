/// Data model for daily market briefing
class Briefing {
  final String date;
  final String usSummary;
  final String? marketSentiment;
  final Map<String, dynamic>? keyIndices;
  final int fearGreedScore;

  Briefing({
    required this.date,
    required this.usSummary,
    this.marketSentiment,
    this.keyIndices,
    this.fearGreedScore = 50,
  });

  factory Briefing.fromJson(Map<String, dynamic> json) {
    return Briefing(
      date: json['date']?.toString() ?? DateTime.now().toIso8601String(),
      usSummary: json['us_summary'] as String? ?? '',
      marketSentiment: json['market_sentiment'] as String?,
      keyIndices: json['key_indices'] as Map<String, dynamic>?,
      fearGreedScore: json['fear_greed_score'] as int? ?? 50,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date,
      'us_summary': usSummary,
      'market_sentiment': marketSentiment,
      'key_indices': keyIndices,
      'fear_greed_score': fearGreedScore,
    };
  }
}

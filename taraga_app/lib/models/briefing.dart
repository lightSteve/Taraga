class Briefing {
  final DateTime date;
  final String usSummary;
  final String? marketSentiment;
  final Map<String, dynamic>? keyIndices;

  Briefing({
    required this.date,
    required this.usSummary,
    this.marketSentiment,
    this.keyIndices,
  });

  factory Briefing.fromJson(Map<String, dynamic> json) {
    return Briefing(
      date: DateTime.parse(json['date']),
      usSummary: json['us_summary'] ?? '',
      marketSentiment: json['market_sentiment'],
      keyIndices: json['key_indices'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'us_summary': usSummary,
      'market_sentiment': marketSentiment,
      'key_indices': keyIndices,
    };
  }
}

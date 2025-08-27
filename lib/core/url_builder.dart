import 'config.dart'; // for baseUrl

String buildVersesUrl({
  required String projectId,
  required String volumeId,
  required String chapterId,
  required String lang,
}) {
  return "$baseUrl/$projectId/volumes/$volumeId/chapters/$chapterId/lang/$lang/verses.txt";
}

String buildMeaningsUrl({
  required String projectId,
  required String volumeId,
  required String chapterId,
  required String lang,
}) {
  return "$baseUrl/$projectId/volumes/$volumeId/chapters/$chapterId/lang/$lang/meanings.txt";
}

String buildDurationsUrl({
  required String projectId,
  required String volumeId,
  required String chapterId,
}) {
  return "$baseUrl/$projectId/volumes/$volumeId/chapters/$chapterId/durations.csv";
}

String buildAudioUrl({
  required String projectId,
  required String volumeId,
  required String chapterId,
  String format = "m4a",
}) {
  return "$baseUrl/$projectId/volumes/$volumeId/chapters/$chapterId/audio.$format";
}

String chapterDescriptionsUrl(String projectId, int volumeIndex) {
  final volId = volumeIndex.toString().padLeft(2, "0");
  return "$baseUrl/$projectId/metadata/volume$volId.txt";
}

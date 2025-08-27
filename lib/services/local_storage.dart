import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

class MeaningStorage {
  static Future<File> _fileForChapter(String volumeId, String chapterId) async {
    final dir = await getApplicationDocumentsDirectory();
    final path = "${dir.path}/meanings/$volumeId";
    await Directory(path).create(recursive: true);
    return File("$path/chapter$chapterId.txt");
  }

  static Future<List<String>> loadMeanings(String volumeId, String chapterId) async {
    try {
      final file = await _fileForChapter(volumeId, chapterId);
      if (await file.exists()) {
        final raw = await file.readAsString();
        final decoded = jsonDecode(raw);
        if (decoded is List) {
          return decoded.map((e) => e.toString()).toList();
        }
      }
      return const [];
    } catch (_) {
      return const [];
    }
  }

  static Future<void> saveMeanings(
      String volumeId, String chapterId, List<String?> lines) async {
    final file = await _fileForChapter(volumeId, chapterId);
    final safe = lines.map((e) => e ?? "").toList(); // replace null with ""
    await file.writeAsString(jsonEncode(safe));
  }
}

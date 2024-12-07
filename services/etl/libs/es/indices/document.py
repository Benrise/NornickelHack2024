index_name = "documents"

index_json = {
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type": "stop",
          "stopwords": "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type": "stop",
          "stopwords": "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "document_id": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "text_content": {
        "type": "text",
        "analyzer": "standard"
      },
      "text_content_vector": {
        "type": "dense_vector",
        "dims": 384
      },
      "metadata": {
        "type": "nested",
        "properties": {
          "author": {
            "type": "text",
            "analyzer": "standard"
          },
          "created_date": {
            "type": "date"
          },
          "tags": {
            "type": "keyword"
          },
          "file_type": {
            "type": "keyword"
          }
        }
      },
      "images": {
        "type": "nested",
        "properties": {
          "image_id": {
            "type": "keyword"
          },
          "ocr_text": {
            "type": "text",
            "analyzer": "standard"
          },
          "position": {
            "type": "keyword"
          },
          "image_path": {
            "type": "keyword"
          }
        }
      }
    }
  }
}

Version 1.2.0
-------------
* Update syntax for json-schema draft 7
* Fix validation rules for "license" property. Prior schema referenced
  a non-existent spdx schema.
* Add "user_docs_url" property.
* Various description string copy edits.
* MaxLength constraints added for all string types
* Extracted #/definitions/url
* Extracted #/definitions/url_multilingual_or_array
* toolinfo_version replaced by $schema
* toolinfo_language replaced by $language

.. literalinclude:: ../jsonschema/toolinfo/1.2.0.json
   :language: JSON

Version 1.1.1
-------------
Updated the schema with new fields while maintaining full backwards
compatibility with the previous schema.

.. literalinclude:: ../jsonschema/toolinfo/1.1.1.json
   :language: JSON

Version 1.0.0
-------------
The initial version of the json schema was reverse engineered from the
toolinfo.json standard described at
https://hay.toolforge.org/directory/#addtool.

.. literalinclude:: ../jsonschema/toolinfo/1.0.0.json
   :language: JSON

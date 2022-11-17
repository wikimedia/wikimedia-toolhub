import i18n from '@/plugins/i18n';

/**
 * Get a human friendly label for a given for_wikis value.
 *
 * @param {string} value - for_wikis value from toolinfo.json
 * @return {string} Label to show to humans
 */
export function forWikiLabel( value ) {
	let lookup = value;
	let parts = value.split( '.' );
	if (
		parts.length === 3 &&
		( parts[ 0 ] === '*' || parts[ 0 ] === 'www' )
	) {
		// Drop leading wildcard or www
		parts = parts.slice( 1 );
		lookup = parts.join( '.' );
	}
	switch ( lookup ) {
		case '*':
			return i18n.t( 'search-filter-wiki-any' );
		case 'commons.wikimedia.org':
		case 'species.wikimedia.org':
		case 'mediawiki.org':
		case 'wikibooks.org':
		case 'wikidata.org':
		case 'wikinews.org':
		case 'wikipedia.org':
		case 'wikiquote.org':
		case 'wikisource.org':
		case 'wikiversity.org':
		case 'wikivoyage.org':
		case 'wiktionary.org':
			// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
			return i18n.t( 'search-filter-wiki-' + parts[ 0 ] );
		default:
			return value;
	}
}

/**
 * Get a localized label for a given enum field value.
 *
 * @param {string} enumName - name of the enum field to localize
 * @param {string} value - enum value
 * @return {string} Localized label to show to humans
 */
export function localizeEnum( enumName, value ) {
	if ( !( typeof enumName === 'string' && typeof value === 'string' ) ) {
		return '';
	}
	const prefix = 'search-filter-' + enumName.replace( /_/g, '-' ) + '-';
	const cleanValue = value.replace( /(\s|::|_)/g, '-' );
	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	return i18n.t( prefix + cleanValue );
}

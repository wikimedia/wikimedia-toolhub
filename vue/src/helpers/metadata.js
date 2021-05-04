import i18n from '@/plugins/i18n';

export function getMetaTitle( pagekey, suffix = false ) {
	const metaTitle = suffix ? 'metadata-title-long' : 'metadata-title-short';
	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	const params = [ i18n.t( pagekey ) ];
	if ( suffix ) {
		params.push( suffix );
	}

	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	return i18n.t( metaTitle, params );
}

export function getMetaDescription( pagekey ) {
	// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
	return i18n.t( 'metadata-' + pagekey + '-description' );
}

export function fetchMetaInfo( pagekey, suffix = false ) {
	return {
		title: getMetaTitle( pagekey, suffix ),
		meta: [
			{
				property: 'og:site_name',
				content: i18n.t( 'metadata-sitename' )
			},
			{
				name: 'description',
				content: getMetaDescription( pagekey )
			},
			{
				name: 'og:description',
				content: getMetaDescription( pagekey )
			},
			{
				property: 'og:url',
				content: window.location.href
			}
		]
	};
}

export default fetchMetaInfo;

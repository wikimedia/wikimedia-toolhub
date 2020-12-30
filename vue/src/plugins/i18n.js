import Vue from 'vue';
import VueI18n from 'vue-i18n';
import FallbackMap from './i18n-fallback';
import BananaFormatter from './i18n-formatter';
import { initialLocale } from '@/store/locale';

Vue.use( VueI18n );

function loadLocaleMessages() {
	const locales = require.context(
		'@/assets/locales/i18n', true, /[A-Za-z0-9-_,\s]+\.json$/i
	);
	const messages = {};
	locales.keys().forEach( ( key ) => {
		const matched = key.match( /([A-Za-z0-9-_]+)\./i );
		if ( matched && matched.length > 1 ) {
			const locale = matched[ 1 ];
			messages[ locale ] = locales( key );
		}
	} );

	// Generate a qqx locale based on the keys found in the en locale.
	messages.qqx = Object.keys( messages.en ).reduce( ( out, val ) => {
		out[ val ] = `(${val})`;
		return out;
	}, {} );

	return messages;
}

export default new VueI18n( {
	locale: initialLocale,
	formatter: new BananaFormatter( initialLocale ),
	fallbackLocale: FallbackMap,
	messages: loadLocaleMessages(),
	silentFallbackWarn: true
} );

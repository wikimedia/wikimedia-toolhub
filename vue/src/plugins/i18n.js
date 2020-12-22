import Vue from 'vue';
import VueI18n from 'vue-i18n';
import FallbackMap from './i18n-fallback';

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
	return messages;
}

/**
 * Select which translation to use for a given value and set of translations.
 *
 * Monkey patch a different implementation of getChoiceIndex over the upstream
 * default. This implementation uses logic equivalent to that from
 * wikimedia/banana-i18n and delegates to Intl.PluralRules for the hard part
 * of knowing which locales have more complex plural forms than ['one',
 * 'other'].
 *
 * @param {number} choice - a choice index given by the input to $tc
 * @param {number} choicesLength - number of translation choices available
 * @return {number} a choice index
 */
VueI18n.prototype.getChoiceIndex = function ( choice, choicesLength ) {
	// Adapted from @wikimedia/banana-i18n's src/languages/language.js
	const number = Math.abs( choice );
	const pluralForms = [ 'zero', 'one', 'two', 'few', 'many', 'other' ];
	const pluralRules = new Intl.PluralRules( this.locale );
	const pluralCategories = pluralRules.resolvedOptions().pluralCategories;
	const form = pluralRules.select( number );
	const pluralFormIndex = pluralForms
		.filter( ( f ) => pluralCategories.indexOf( f ) !== -1 )
		.indexOf( form );
	return Math.min( pluralFormIndex, choicesLength - 1 );
};

export default new VueI18n( {
	locale: navigator.language.split( '-' )[ 0 ],
	fallbackLocale: FallbackMap,
	messages: loadLocaleMessages(),
	silentFallbackWarn: true
} );

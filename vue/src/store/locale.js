import Vue from 'vue';
import Vuex from 'vuex';
import languageData from '@wikimedia/language-data';

Vue.use( Vuex );

// T269164: Add a qqx mapping to languageNameMap.
languageData.addLanguage(
	'qqx',
	{ script: 'Latn', regions: [], autonym: 'QQX' }
);

export const DEFAULT_LOCALE = 'en';
export const LOCALE_KEY = 'locale';

/**
 * @param {string} locale
 * @return {string}
 */
export function santizeLocale( locale ) {
	if ( languageData.isKnown( locale ) ) {
		return languageData.isRedirect( locale ) || locale;
	}
	let parts = String( locale ).toLowerCase().split( '-' );
	while ( parts && parts.length ) {
		const code = parts.join( '-' );
		if ( languageData.isKnown( code ) ) {
			return languageData.isRedirect( code ) || code;
		}
		parts = parts.slice( 0, -1 );
	}
	return DEFAULT_LOCALE;
}

export const initalLocale = ( () => {
	return santizeLocale(
		window.localStorage.getItem( LOCALE_KEY ) ||
		window.navigator.language ||
		DEFAULT_LOCALE
	);
} )();

const localeMap = ( () => {
	const popularLocales = [ 'en' ];
	const languageNameMap = languageData.getAutonyms();

	const filteredLocales = popularLocales.reduce( ( obj, key ) => {
		obj[ key ] = languageNameMap[ key ];
		return obj;
	}, {} );

	return {
		...filteredLocales,
		...languageNameMap
	};
} )();

export const getters = {
	/**
	 * Get autonym of active locale.
	 *
	 * @param {Object} state
	 * @return {string}
	 */
	localeAutonym( state ) {
		return languageData.getAutonym( state.locale );
	}
};

export const actions = {
	/**
	 * Initialize the locale.
	 *
	 * Intended to be called from the application's `created()` callback.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {Object} payload.vm - Vue
	 * @return {Promise}
	 */
	initializeLocale( context, payload ) {
		payload.initial = true;
		payload.locale = initalLocale;
		const qs = payload.vm.$route.query;
		if ( qs.uselang ) {
			payload.locale = santizeLocale( qs.uselang );
		}
		return context.dispatch( 'setLocale', payload );
	},

	/**
	 * Trigger a locale change.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {string} payload.locale - ISO 639-1 code
	 * @param {Object} payload.vm - Vue
	 * @param {boolean} payload.initial - Are we being called by the intializer?
	 * @return {Promise}
	 */
	setLocale( context, payload ) {
		const locale = santizeLocale( payload.locale );
		const vm = payload.vm;
		const initial = payload.initial || false;

		return context.dispatch(
			'user/setLocale', locale, { root: true }
		).then( () => {
			context.commit( 'onLocaleChanged', { locale: locale } );

			// Set the locale for the frontend
			vm.$i18n.locale = locale;
			vm.$vuetify.rtl = languageData.isRtl( locale );

			// Show the locale in the query string if it changed
			if ( !initial && vm.$route.query.uselang !== locale ) {
				vm.$router.push( { query: { uselang: locale } } );
			}
		} );
	}
};

export const mutations = {
	/**
	 * Persist a locale change.
	 *
	 * @param {Object} state - Vuex state tree.
	 * @param {Object} payload - mutation payload.
	 * @param {string} payload.locale - ISO 639-1 code.
	 */
	onLocaleChanged( state, payload ) {
		window.localStorage.setItem( LOCALE_KEY, payload.locale );
		state.locale = payload.locale;
	}
};

export default {
	namespaced: true,
	state: {
		locale: initalLocale,
		localeMap: localeMap
	},
	getters: getters,
	actions: actions,
	mutations: mutations,
	strict: process.env.NODE_ENV !== 'production'
};

<template>
	<v-menu max-height="250" offset-y>
		<template #activator="{ on, attrs }">
			<v-btn
				class="ma-1 transparent elevation-0"
				v-bind="attrs"
				v-on="on"
			>
				<v-icon class="me-2">
					mdi-translate
				</v-icon>
				{{ currentLocaleNativeLabel }}
			</v-btn>
		</template>
		<v-list>
			<v-list-item
				v-for="(language, code) in languages"
				:key="code"
				selectable
				link
			>
				<v-list-item-title
					@click="setLocale( code, language )"
				>
					{{ language.native }} ({{ code }})
				</v-list-item-title>
			</v-list-item>
		</v-list>
	</v-menu>
</template>

<script>
import languageNameMap from 'language-name-map/map';

// T269164: Add a qqx mapping to languageNameMap.
languageNameMap.qqx = { name: 'QQX', dir: 1, native: 'QQX' };

/**
 * Lookup a Locale model.
 *
 * @param {string} code - Locale name to lookup (e.g. en-US-southern)
 * @return {Object} Locale
 */
function findLocaleForCode( code ) {
	const tokens = code.toLowerCase().split( '-' );
	while ( tokens.length ) {
		const lookup = tokens.join( '-' );
		if ( lookup in languageNameMap ) {
			return languageNameMap[ lookup ];
		}
		tokens.splice( -1, 1 );
	}
	// Fallback to English as a last resort
	return languageNameMap.en;
}

export default {
	name: 'SelectLocale',
	data() {
		return {
			currentLocaleNativeLabel: ''
		};
	},
	computed: {
		languages() {
			const popularLocales = [ 'en' ];
			const filteredLocales = popularLocales.reduce( ( obj, key ) => {
				obj[ key ] = languageNameMap[ key ];
				return obj;
			}, {} );

			return {
				...filteredLocales,
				...languageNameMap
			};
		}
	},
	methods: {
		setLocale( code, locale ) {
			if ( this.$i18n.locale === code ) {
				return;
			}

			// Set the locale for the frontend
			this.$i18n.locale = code;
			this.$vuetify.rtl = ( locale.dir === 0 );
			// Set the locale for the backend
			this.$store.dispatch( 'user/setLocale', code );
			// Set the display label for the active locale
			this.currentLocaleNativeLabel = locale.native;

			// Show the locale in the query string if it changed
			if ( this.$route.query.uselang !== code ) {
				this.$router.push( {
					query: { uselang: code }
				} );
			}
		}
	},
	watch: {
		'$route.query': {
			immediate: true,
			handler( qs ) {
				if ( qs.uselang ) {
					const locale = findLocaleForCode( qs.uselang );
					this.setLocale( qs.uselang, locale );
				}
			}
		}
	},
	mounted() {
		const locale = findLocaleForCode(
			this.$route.query.uselang || this.$i18n.locale
		);
		this.currentLocaleNativeLabel = locale.native;
	}
};
</script>

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
				v-for="(label, code) in languages"
				:key="code"
				selectable
				link
			>
				<v-list-item-title
					@click="setLocale( code )"
				>
					{{ label }} ({{ code }})
				</v-list-item-title>
			</v-list-item>
		</v-list>
	</v-menu>
</template>

<script>
import languageData from '@wikimedia/language-data';

const languageNameMap = languageData.getAutonyms();

// T269164: Add a qqx mapping to languageNameMap.
languageNameMap.qqx = 'QQX';

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
		setLocale( code ) {
			// TODO: move this logic into vuex?
			if ( this.$i18n.locale === code ) {
				return;
			}

			if ( !languageData.isKnown( code ) && code !== 'qqx' ) {
				return;
			}

			const direction = languageData.getDir( code );
			const autonym = languageData.getAutonym( code );

			// Set the locale for the frontend
			this.$i18n.locale = code;
			this.$vuetify.rtl = ( direction === 'rtl' );
			// Set the locale for the backend
			this.$store.dispatch( 'user/setLocale', code );
			// Set the display label for the active locale
			this.currentLocaleNativeLabel = autonym;

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
				if ( qs.uselang !== this.$i18n.locale ) {
					this.setLocale( qs.uselang );
				}
			}
		}
	},
	mounted() {
		this.currentLocaleNativeLabel = languageData.getAutonym(
			this.$i18n.locale
		);
	}
};
</script>

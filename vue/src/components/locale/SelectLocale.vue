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
				{{ curLocaleNative }}
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

export default {
	name: 'SelectLocale',
	data() {
		return {
			curLocaleNative: ''

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

			this.$i18n.locale = code;
			this.curLocaleNative = locale.native;
			this.$store.dispatch( 'user/setLocale', code );
			this.$router.push( {
				query: { locale: code }
			} );

			this.$vuetify.rtl = ( locale.dir === 0 );
		}
	},
	mounted() {
		const curLocaleCode = this.$i18n.locale,
			curLocale = this.languages && this.languages[ curLocaleCode ];

		this.curLocaleNative = curLocale && curLocale.native;
	}
};
</script>

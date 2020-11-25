<template>
	<v-menu max-height="250" offset-y>
		<template #activator="{ on, attrs }">
			<p class="font-weight-bold mt-4 mr-3">
				{{ $i18n.locale }}
			</p>

			<v-btn
				icon
				v-bind="attrs"
				v-on="on"
			>
				<v-icon>
					mdi-translate
				</v-icon>
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
					@click="setLocale(code, language.dir)"
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
			languages: languageNameMap
		};
	},
	methods: {
		setLocale( locale, dir ) {
			if ( this.$i18n.locale === locale ) {
				return;
			}

			this.$i18n.locale = locale;
			this.$store.dispatch( 'setLocale', locale );
			this.$router.push( {
				query: { locale: locale }
			} );

			this.$vuetify.rtl = ( dir === 0 );
		}
	}
};
</script>

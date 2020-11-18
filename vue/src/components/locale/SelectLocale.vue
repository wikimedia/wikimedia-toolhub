<template>
	<v-col ma-6
		lg="2"
		md="3"
		sm="4"
		cols="5"
	>
		<v-select
			v-model="$i18n.locale"
			:items="languages"
			:item-text="item => item.name + ' (' + item.code + ') '"
			:item-value="'code'"
			prepend-icon="mdi-web"
			menu-props="auto"
			hide-details
			:label="$t( 'selectlanguage' )"
			single-line
			@change="setLocale"
		/>
	</v-col>
</template>

<script>
import languages_json from '@/assets/locales/languages.json';

export default {
	name: 'SelectLocale',
	data() {
		return {
			languages: languages_json
		};
	},
	methods: {
		setLocale( locale ) {
			this.$i18n.locale = locale;
			this.$router.push( {
				query: { locale: locale }
			} );
		}
	}
};
</script>

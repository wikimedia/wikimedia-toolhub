<template>
	<v-menu offset-y>
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
				v-for="(language, index) in languages"
				:key="index"
				selectable
				link
			>
				<v-list-item-title
					@click="setLocale(language.code)"
				>
					{{ language.name }} ({{ language.code }})
				</v-list-item-title>
			</v-list-item>
		</v-list>
	</v-menu>
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
			if ( this.$i18n.locale === locale ) {
				return;
			}

			this.$i18n.locale = locale;
			this.$router.push( {
				query: { locale: locale }
			} );
		}
	}
};
</script>

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
				{{ localeAutonym }}
			</v-btn>
		</template>
		<v-list>
			<v-list-item
				v-for="(label, code) in localeMap"
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
import { mapGetters, mapState } from 'vuex';

export default {
	name: 'SelectLocale',
	computed: {
		...mapState( 'locale', [ 'locale', 'localeMap' ] ),
		...mapGetters( 'locale', [ 'localeAutonym' ] )
	},
	methods: {
		setLocale( code ) {
			if ( this.$i18n.locale === code ) {
				return;
			}

			this.$store.dispatch(
				'locale/setLocale', { locale: code, vm: this }
			);
		}
	}
};
</script>

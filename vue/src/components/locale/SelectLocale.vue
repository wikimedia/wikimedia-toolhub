<template>
	<v-dialog
		v-model="dialog"
		scrollable
		transition="dialog-bottom-transition"
		width="300"
		content-class="locale-select"
	>
		<template #activator="{ on, attrs }">
			<v-btn
				class="ma-1 transparent elevation-0"
				v-bind="attrs"
				v-on="on"
			>
				<v-icon
					:title="localeAutonym"
					class="me-2"
				>
					mdi-translate
				</v-icon>
				{{ localeAutonym }}
			</v-btn>
		</template>
		<v-card>
			<v-toolbar
				dark
				color="secondary"
			>
				<v-text-field
					v-model="searchString"
					:label="$t( 'locale-select' )"
					clearable
					single-line
					@input="onSearch"
					@click:clear="onClear"
				>
					<template #prepend>
						<v-icon>mdi-magnify</v-icon>
					</template>
				</v-text-field>
				<v-spacer />
				<v-btn
					icon
					@click="dialog = false"
				>
					<v-icon>mdi-close-box-outline</v-icon>
				</v-btn>
			</v-toolbar>
			<v-card-text
				class="selectlocale-body"
			>
				<v-list>
					<v-list-item
						v-for="(autonym, code) in filteredLocales || localeMap"
						:key="code"
						selectable
						link
					>
						<v-list-item-content
							@click="setLocale( code )"
						>
							<dl class="row mx-0">
								<dt class="me-1">{{ autonym }}</dt>
								<dd>({{ code }})</dd>
							</dl>
						</v-list-item-content>
					</v-list-item>
				</v-list>
			</v-card-text>
			<v-toolbar>
				<v-btn
					class="ma-1 transparent elevation-0 text-capitalize"
					href="https://translatewiki.net/w/i.php?title=Special:Translate&group=toolhub"
				>
					{{ $t( 'helptranslate' ) }}
				</v-btn>
			</v-toolbar>
		</v-card>
	</v-dialog>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
	name: 'SelectLocale',
	data: () => ( {
		dialog: false,
		searchString: '',
		filteredLocales: null
	} ),
	computed: {
		...mapState( 'locale', [ 'locale', 'localeMap' ] ),
		...mapGetters( 'locale', [ 'localeAutonym' ] )
	},
	methods: {
		setLocale( code ) {
			this.$store.dispatch(
				'locale/setLocale', { locale: code, vm: this }
			);
			this.dialog = false;
		},
		onSearch() {
			if ( !this.searchString ) {
				this.filteredLocales = null;
				return;
			}
			const query = new RegExp(
				this.searchString.replace( /[.*+?^${}()|[\]\\]/g, '\\$&' ),
				'iu'
			);
			this.filteredLocales = {};
			Object.keys( this.localeMap ).forEach( ( key ) => {
				if (
					query.test( key ) ||
					query.test( this.localeMap[ key ] )
				) {
					this.filteredLocales[ key ] = this.localeMap[ key ];
				}
			} );
		},
		onClear() {
			this.searchString = '';
			this.onSearch();
		}
	}
};
</script>

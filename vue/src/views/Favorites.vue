<template>
	<v-container>
		<v-row>
			<v-col>
				<h2 class="text-h4">
					{{ $t( 'favorites-pagetitle' ) }}
				</h2>
			</v-col>
		</v-row>
		<v-row v-if="favoriteTools.length === 0">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'favorites-notoolsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row class="my-2">
			<v-col v-for="tool in favoriteTools"
				:key="tool.name"
				class="lists pa-0"
			>
				<v-card
					class="ma-4"
					min-width="210"
				>
					<ToolCard :tool="tool" />
				</v-card>
			</v-col>
		</v-row>
		<v-pagination
			v-if="numFavoriteTools > 0"
			v-model="page"
			:length="Math.ceil( numFavoriteTools / itemsPerPage )"
			class="ma-4"
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import ToolCard from '@/components/tools/ToolCard';

export default {
	components: {
		ToolCard
	},
	data() {
		return {
			page: 1,
			itemsPerPage: 10
		};
	},
	computed: {
		...mapState( 'favorites', [ 'favoriteTools', 'numFavoriteTools' ] )
	},
	methods: {
		getFavoriteTools() {
			this.$store.dispatch( 'favorites/getFavoriteTools', this.page );
		},
		goToPage( num ) {
			const query = { page: parseInt( num ) || 1 };
			this.$router.push( { query } ).catch( () => {} );
		}
	},
	watch: {
		/**
		 * Watch ?page=... and update favorite tools.
		 *
		 * @param {string} newValue
		 */
		'$route.query.page'( newValue ) {
			this.page = parseInt( newValue ) || 1;
			this.getFavoriteTools();
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;
		this.getFavoriteTools();
	}
};
</script>

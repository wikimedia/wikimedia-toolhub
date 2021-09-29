<template>
	<v-btn
		v-if="userAuthed && favorite"
		:small="$vuetify.breakpoint.smAndDown"
		class="ms-4"
		color="yellow50"
		@click="removeFavorite"
	>
		<v-icon class="me-2">
			mdi-star
		</v-icon>
		{{ $t( 'favorited' ) }}
	</v-btn>
	<v-btn
		v-else-if="userAuthed"
		:small="$vuetify.breakpoint.smAndDown"
		class="ms-4"
		@click="addFavorite"
	>
		<v-icon class="me-2">
			mdi-star-outline
		</v-icon>
		{{ $t( 'favorite' ) }}
	</v-btn>
</template>

<script>
import { mapActions } from 'vuex';

export default {
	name: 'FavoriteButton',
	props: {
		tool: {
			type: Object,
			default: null
		}
	},
	data() {
		return {
			clicks: 0,
			userAuthed: this.$can( 'add', 'lists/toollist' )
		};
	},
	asyncComputed: {
		favorite: {
			get() {
				if ( this.userAuthed && this.tool ) {
					return this.isFavorite( this.tool.name );
				}
				return false;
			},
			default: false,
			// Each time the value of this.clicks changes, this property
			// will be recomputed and related state dynamically updated.
			watch: [ 'clicks' ]
		}
	},
	methods: {
		...mapActions( 'favorites', [ 'isFavorite' ] ),
		/**
		 * Add the current tool to the user's favorites.
		 */
		addFavorite() {
			this.$store.dispatch( 'favorites/addTool', this.tool.name ).then(
				() => { this.clicks++; }
			);
		},
		/**
		 * Remove the current tool from the user's favorites.
		 */
		removeFavorite() {
			this.$store.dispatch( 'favorites/removeTool', this.tool.name ).then(
				() => { this.clicks++; }
			);
		}
	}
};
</script>

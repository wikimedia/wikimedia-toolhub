<template>
	<v-container>
		<v-row>
			<v-col>
				<h2 class="text-h4">
					{{ $t( 'lists-yourlists' ) }}
				</h2>
			</v-col>

			<v-col
				cols="auto"
			>
				<v-btn
					color="primary base100--text"
					:to="{ name: 'lists-create' }"
				>
					<v-icon>
						mdi-plus
					</v-icon>
					{{ $t( 'lists-createnewlist' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<Lists
			:lists="myLists"
			@delete-list="deleteList( $event )"
		/>
		<v-row v-if="!myLists.count">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'lists-nolistsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-pagination
			v-if="myLists.count > 0"
			v-model="page"
			:length="Math.ceil( myLists.count / itemsPerPage )"
			class="ma-4"
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import fetchMetaInfo from '@/helpers/metadata';
import { mapState } from 'vuex';
import Lists from '@/components/lists/Lists';

export default {
	components: {
		Lists
	},
	data() {
		return {
			page: 1,
			itemsPerPage: 10
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'lists' );
	},
	computed: {
		...mapState( 'lists', [ 'myLists' ] )
	},
	methods: {
		getMyLists() {
			this.$store.dispatch( 'lists/getMyLists', this.page );
		},
		goToPage( num ) {
			const query = { page: parseInt( num ) || 1 };
			this.$router.push( { query } ).catch( () => {} );
		},
		deleteList( id ) {
			this.$store.dispatch( 'lists/deleteList', id ).then(
				() => {
					const currentPage = this.page;
					const lastPage = this.page === 1 ? 1 : Math.ceil(
						( this.myLists.count - 1 ) / this.itemsPerPage );
					this.page = Math.min( this.page, lastPage );
					if ( this.page !== currentPage ) {
						this.$router.push( { path: 'lists', query: { page: this.page } } );
					}
					this.getMyLists();
				}
			);
		}
	},
	watch: {
		/**
		 * Watch ?page=... and update private lists.
		 *
		 * @param {string} newValue
		 */
		'$route.query.page'( newValue ) {
			this.page = parseInt( newValue ) || 1;
			this.getMyLists();
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;
		this.getMyLists();
	}
};
</script>

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

		<v-row v-if="!myLists.results">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'lists-nolistsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in myLists.results"
				:key="list.id"
				class="lists"
				cols="12"
			>
				<ListCard :list="list" />
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
import ListCard from '@/components/lists/ListCard';

export default {
	components: {
		ListCard
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

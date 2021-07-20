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
					to="/lists/create"
				>
					<v-icon>
						mdi-plus
					</v-icon>
					{{ $t( 'lists-createnewlist' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row v-if="privateLists.count === 0">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'lists-nolistsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in privateLists.results"
				:key="list.title"
				class="lists"
				cols="12"
			>
				<ListView :list="list" />
			</v-col>
		</v-row>

		<v-pagination
			v-if="privateLists.count > 0"
			v-model="page"
			:length="Math.ceil( privateLists.count / itemsPerPage )"
			class="ma-4"
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import fetchMetaInfo from '@/helpers/metadata';
import { mapState } from 'vuex';
import ListView from '@/components/lists/ListView';

export default {
	components: {
		ListView
	},
	data() {
		return {
			tabs: null,
			page: 1,
			itemsPerPage: 10
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'lists' );
	},
	computed: {
		...mapState( 'lists', [ 'privateLists' ] )
	},
	methods: {
		getPrivateLists() {
			this.$store.dispatch( 'lists/getPrivateLists', this.page );
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
			this.getPrivateLists();
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;
		this.getPrivateLists();
	}
};
</script>

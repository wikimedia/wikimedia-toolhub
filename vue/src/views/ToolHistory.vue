<template>
	<v-container>
		<v-row>
			<v-col md="9" cols="12">
				<h2 class="text-h4">
					{{ $t( 'tools-history' ) }}
				</h2>
			</v-col>

			<v-col md="3" cols="12">
				<v-btn
					:to="{ name: 'tools-view', params: { name: name } }"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolinfo' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'toolhistory-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<Revisions
					:revisions="toolRevisions"
					:page="page"
					@update-revisions="getRevisions"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-pagination
					v-if="numRevisions > 0"
					v-model="page"
					:length="Math.ceil( numRevisions / itemsPerPage )"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import fetchMetaInfo from '@/helpers/metadata';
import Revisions from '@/components/common/Revisions';

export default {
	name: 'ToolHistory',
	components: {
		Revisions
	},
	data() {
		return {
			name: this.$route.params.name,
			page: 1,
			itemsPerPage: 10
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'tools-history', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'toolRevisions', 'numRevisions' ] )
	},
	methods: {
		getRevisions() {
			this.$store.dispatch( 'tools/updateToolRevisions', {
				page: this.page, name: this.name
			} );
		},
		goToPage( page ) {
			this.page = page;
			this.getRevisions();
		}
	},
	mounted() {
		this.getRevisions();
	}
};
</script>

<template>
	<v-container v-if="changes">
		<v-row>
			<v-col md="9" cols="12">
				<h2 class="text-h4">
					{{ $t( 'tools-diff' ) }}
				</h2>
			</v-col>

			<v-col md="3" cols="12">
				<v-btn
					:to="{ name: 'tools-history', params: { name: name } }"
					:small="$vuetify.breakpoint.smAndDown"
				>
					<v-icon class="me-2">
						mdi-chevron-left
					</v-icon>
					{{ $t( 'backtotoolhistory' ) }}
				</v-btn>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				{{ $t( 'viewtoolrevisionsdiff', [ name ] ) }}
			</v-col>
		</v-row>

		<v-row v-if="diffRevision"
			class="my-4"
		>
			<v-col cols="6">
				<h3 class="font-weight-medium">
					{{ $t( 'toolrevisioninfo', [
						formatDate( diffRevision.original.timestamp ),
						diffRevision.original.user.username,
						diffRevision.original.comment
					] ) }}
				</h3>
			</v-col>
			<v-col cols="6">
				<h3 class="font-weight-medium">
					{{ $t( 'toolrevisioninfo', [
						formatDate( diffRevision.result.timestamp ),
						diffRevision.result.user.username,
						diffRevision.result.comment
					] ) }}
				</h3>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12" class="my-2">
				<v-row v-for="( op, idx ) in changes"
					:key="idx"
				>
					<v-col cols="6">
						<v-row class="ms-2 cols">
							<DiffPath :path="op.path" />
						</v-row>
						<DiffValue op="remove" :value="op.oldValue" />
					</v-col>
					<v-col cols="6">
						<v-row class="ms-2 cols">
							<DiffPath :path="op.path" />
						</v-row>
						<DiffValue op="add" :value="op.newValue" />
					</v-col>
				</v-row>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapMutations } from 'vuex';
import { normalizeEmpty, computeChangeInfo } from '@/helpers/diff';
import { fetchMetaInfo } from '@/helpers/metadata';
import DiffPath from '@/components/diff/DiffPath';
import DiffValue from '@/components/diff/DiffValue';

export default {
	name: 'ToolRevisionsDiff',
	components: {
		DiffPath,
		DiffValue
	},
	data() {
		return {
			name: this.$route.params.name,
			revId: this.$route.params.revId,
			otherRevId: this.$route.params.otherRevId
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'tools-diff', this.name );
	},
	computed: {
		...mapState( 'tools', [ 'diffRevision', 'toolRevision' ] ),
		/**
		 * Compute changes to render as diff based on JSON Patch from API.
		 *
		 * @return {Object[]}
		 */
		changes() {
			if ( !this.diffRevision || !this.toolRevision ) {
				return [];
			}
			return computeChangeInfo(
				this.diffRevision.operations,
				this.toolRevision.toolinfo,
				this.formatProperty
			);
		}
	},
	methods: {
		...mapMutations( 'tools', [ 'DIFF_REVISION' ] ),
		getDiff() {
			this.$store.dispatch( 'tools/getToolRevisionsDiff', {
				name: this.name,
				revId: this.revId,
				otherId: this.otherRevId
			} );
		},
		getRevision() {
			this.$store.dispatch( 'tools/getToolRevision', {
				name: this.name,
				revId: this.revId
			} );
		},
		/**
		 * Format a property value for display to the user.
		 *
		 * @param {string} pointer - JSON-Pointer to property
		 * @param {*} value - property value
		 * @return {*}
		 */
		formatProperty( pointer, value ) {
			if ( pointer.indexOf( 'date' ) !== -1 ) {
				value = this.formatDate( value );
			}
			return normalizeEmpty( value );
		},
		formatDate( date ) {
			return this.$moment.utc( date ).format( 'lll' );
		}
	},
	mounted() {
		// Clear any data from a prior view
		this.DIFF_REVISION( null );
		this.getDiff();
		this.getRevision();
	}
};
</script>

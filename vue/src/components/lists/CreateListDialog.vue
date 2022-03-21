<template>
	<v-dialog
		v-if="schema"
		v-model="show"
		max-width="600px"
	>
		<v-card class="px-6 py-4">
			<v-form ref="createlistform" v-model="valid">
				<v-row dense class="my-4">
					<v-col
						cols="12"
						class="pe-4"
					>
						<v-row class="cols">
							<v-col
								v-for="( uischema, id ) in layout"
								:key="id"
								cols="12"
							>
								<InputWidget
									v-model="listinfo[ id ]"
									:schema="schema.properties[ id ]"
									:ui-schema="uischema"
								/>
							</v-col>
						</v-row>
					</v-col>
				</v-row>
			</v-form>
			<AgreeTerms />
			<v-card-actions>
				<v-btn
					color="primary base100--text"
					class="pa-4"
					:disabled="!valid || !$can( 'add', 'lists/toollist' )"
					@click="createList"
					@click.stop="show = false"
				>
					{{ $t( 'lists-createnewlist' ) }}
				</v-btn>
				<v-btn color="primary"
					text
					@click.stop="show = false"
				>
					{{ $t( 'close' ) }}
				</v-btn>
			</v-card-actions>
		</v-card>
	</v-dialog>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/common/InputWidget';
import AgreeTerms from '@/components/common/AgreeTerms';

export default {
	name: 'CreateListDialog',
	components: {
		AgreeTerms,
		InputWidget
	},
	props: {
		value: {
			type: Boolean
		},
		tool: {
			type: Object,
			default: null
		}
	},
	data() {
		return {
			valid: false,
			listinfo: {
				title: null,
				description: null,
				icon: null,
				tools: [],
				published: false
			}
		};
	},
	computed: {
		...mapState( 'lists', [ 'listCreated' ] ),

		show: {
			get() {
				return this.value;
			},
			set( value ) {
				this.$emit( 'input', value );
			}
		},
		layout() {
			return {
				title: {
					icon: 'mdi-pencil-outline',
					label: this.$t( 'title' ),
					required: true
				},
				description: {
					icon: 'mdi-note-text-outline',
					label: this.$t( 'description' )
				},
				icon: {
					icon: 'mdi-view-list',
					label: this.$t( 'icon' )
				},
				tools: {
					widget: 'multi-select-tool',
					icon: 'mdi-tools',
					label: this.$t( 'lists-create-tools' )
				},
				published: {
					widget: 'checkbox',
					label: this.$t( 'lists-create-published' )
				}
			};
		}
	},
	asyncComputed: {
		schema: {
			get() {
				return this.getRequestSchema( 'lists_create' );
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),

		createList() {
			const newlist = { ...this.listinfo };

			newlist.comment = this.$t(
				'lists-create-comment', [ newlist.title ]
			);

			this.$store.dispatch( 'lists/createNewList', newlist ).then(
				() => {
					if ( this.listCreated ) {
						this.$refs.createlistform.reset();
						this.$store.dispatch( 'lists/getMyLists', { page: 1, pageSize: 10 } );
					}
				}
			);
		}
	},
	mounted() {
		this.listinfo.tools.push( this.tool.name );
	}
};
</script>

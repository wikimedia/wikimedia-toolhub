<template>
	<v-container v-if="schema">
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					<template v-if="listId">
						{{ $t( 'lists-editlist' ) }}
					</template>
					<template v-else>
						{{ $t( 'lists-createnewlist' ) }}
					</template>
				</h2>
			</v-col>
		</v-row>

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

		<v-row>
			<v-col cols="12">
				<template v-if="listId">
					<v-btn
						class="ma-4 pa-4"
						@click="cancelEdit"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-cancel
						</v-icon>
						{{ $t( 'cancel' ) }}
					</v-btn>
					<v-btn
						color="primary base100--text"
						class="pa-4"
						:disabled="!valid || !$can( 'change', 'lists/toollist' )"
						@click="commentDialog = true"
					>
						<v-icon
							dark
							class="me-2"
						>
							mdi-content-save-edit
						</v-icon>
						{{ $t( 'publishchanges' ) }}
					</v-btn>
				</template>

				<template v-else>
					<AgreeTerms />
					<v-btn
						color="primary base100--text"
						class="pa-4"
						:disabled="!valid || !$can( 'add', 'lists/toollist' )"
						@click="createList"
					>
						{{ $t( 'lists-createnewlist' ) }}
					</v-btn>
				</template>
			</v-col>
		</v-row>
		<CommentDialog v-if="listId"
			v-model="commentDialog"
			@save="editList"
		/>
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/common/InputWidget';
import CommentDialog from '@/components/common/CommentDialog';
import AgreeTerms from '@/components/common/AgreeTerms';

export default {
	name: 'CreateEditList',
	components: {
		InputWidget,
		CommentDialog,
		AgreeTerms
	},
	data() {
		return {
			listId: this.$route.params.id,
			valid: false,
			listinfo: {
				title: null,
				description: null,
				icon: null,
				tools: [],
				published: false
			},
			commentDialog: false
		};
	},
	computed: {
		...mapState( 'lists', [ 'listCreated', 'list' ] ),

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
						this.$router.push( { name: 'lists' } );
					}
				}
			);
		},

		editList( comment ) {
			const newlist = { ...this.listinfo };
			newlist.comment = comment;

			this.$store.dispatch( 'lists/editList', newlist ).then(
				() => {
					this.$router.back();
				}
			);

			this.commentDialog = false;
		},
		cancelEdit() {
			this.$router.back();
		},
		getListInfo( id ) {
			this.$store.dispatch( 'lists/getListById', id ).then(
				() => {
					if ( this.list ) {
						this.listinfo = JSON.parse( JSON.stringify( this.list ) );
						this.listinfo.tools = [];

						this.list.tools.forEach( ( tool ) => {
							this.listinfo.tools.push( tool.name );
						} );
					}
				}
			);
		}
	},
	mounted() {
		if ( this.listId ) {
			this.getListInfo( this.listId );
		}
	}
};
</script>

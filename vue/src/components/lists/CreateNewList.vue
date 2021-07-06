<template>
	<v-container v-if="schema">
		<v-row>
			<v-col cols="12" class="text-h5 mt-4">
				{{ $t( 'lists-createnewlist' ) }}
			</v-col>

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

			<v-col cols="12" lg="8">
				<v-btn
					color="primary"
					class="pa-4"
					:disabled="!valid || !$can( 'add', 'lists/toollist' )"
					@click="createList"
				>
					{{ $t( 'lists-createnewlist' ) }}
				</v-btn>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import InputWidget from '@/components/common/InputWidget';

export default {
	name: 'CreateNewList',
	components: {
		InputWidget
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
			},
			layout: {
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
					widget: 'multi-select',
					icon: 'mdi-tools',
					label: this.$t( 'lists-create-tools' ),
					required: true
				},
				published: {
					widget: 'checkbox',
					label: this.$t( 'lists-create-published' )
				}
			}
		};
	},
	computed: {
		...mapState( 'lists', [ 'listCreated' ] )
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
						this.$router.push( { path: '/lists' } );
					}
				}
			);
		}
	}
};
</script>

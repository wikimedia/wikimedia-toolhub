<template>
	<div>
		<v-menu
			left
			offset-y
			:close-on-content-click="false"
		>
			<template #activator="{ on, attrs }">
				<v-btn
					v-if="userAuthed"
					:class="{ 'ms-2': !smallicon }"
					:small="$vuetify.breakpoint.smAndDown || smallicon"
					:icon="smallicon"
					v-bind="attrs"
					v-on="on"
					@click.prevent="getMyLists"
				>
					<v-icon>mdi-dots-vertical</v-icon>
				</v-btn>
			</template>

			<v-card
				class="mx-auto"
				width="250px"
				tile
			>
				<v-list nav
					dense
					class="overflow-y-auto"
					max-height="250px"
				>
					<v-subheader class="text-subtitle-1 primary--text">
						{{ $t( 'lists' ) }}
					</v-subheader>
					<v-list-item-group
						v-model="selectedList"
						color="primary"
					>
						<v-subheader v-if="!myLists.count"
							class="text-subtitle-2 font-weight-light"
						>
							{{ $t( 'lists-nouserlists' ) }}
						</v-subheader>
						<v-list-item
							v-for="list in myLists.results"
							:key="list.id"
							class="text-body-1"
							@click="updateToolList( list )"
						>
							<v-list-item-content>
								<v-list-item-title>{{ list.title }}</v-list-item-title>
							</v-list-item-content>
							<v-list-item-icon v-if="listHasTool( list.id )">
								<v-icon
									small
									color="primary"
								>
									mdi-check
								</v-icon>
							</v-list-item-icon>
						</v-list-item>
					</v-list-item-group>
				</v-list>
				<v-divider />
				<v-list
					nav
					dense
				>
					<v-list-item-group
						color="primary"
					>
						<v-list-item
							v-for="( item, i ) in items"
							:key="i"
						>
							<v-list-item-icon>
								<v-icon> {{ item.icon }} </v-icon>
							</v-list-item-icon>

							<v-list-item-content>
								<v-list-item-title
									@click="showCreateListDialog = true"
								>
									{{ item.text }}
								</v-list-item-title>
							</v-list-item-content>
						</v-list-item>
					</v-list-item-group>
				</v-list>
			</v-card>
		</v-menu>
		<CreateListDialog v-model="showCreateListDialog" :tool="tool" />
	</div>
</template>

<script>
import { mapState } from 'vuex';
import CreateListDialog from '@/components/lists/CreateListDialog.vue';

export default {
	name: 'ToolMenu',
	components: {
		CreateListDialog
	},
	props: {
		tool: {
			type: Object,
			required: true
		},
		smallicon: {
			type: Boolean
		}
	},
	data() {
		return {
			userAuthed: this.$can( 'add', 'lists/toollist' ),
			page: 1,
			pageSize: 20,
			selectedList: null,
			showCreateListDialog: false
		};

	},
	computed: {
		...mapState( 'lists', [ 'myLists' ] ),

		items() {
			return {
				createList: {
					text: this.$t( 'lists-createnewlist' ),
					icon: 'mdi-playlist-plus'
				}
			};
		}
	},
	methods: {
		getMyLists() {
			this.$store.dispatch( 'lists/getMyLists', { page: this.page, pageSize: this.pageSize } ).then(
				() => {
					// If the user has more than 20 lists, get all of them
					if ( this.myLists.count > this.pageSize ) {
						this.pageSize = this.myLists.count;
						this.getMyLists();
					}
				}
			);
		},
		getListById( id ) {
			return this.myLists.results.find( ( list ) => list.id === id );
		},
		listHasTool( listId ) {
			const toolList = this.getListById( listId ).tools;
			return Object.keys( toolList ).some( ( key ) =>
				toolList[ key ].name === this.tool.name );
		},
		updateToolList( list ) {
			const newlist = { ...this.getListById( list.id ) };
			const tools = [];
			newlist.tools.forEach( ( tool ) => {
				tools.push( tool.name );
			} );
			newlist.tools = tools;
			if ( !this.listHasTool( list.id ) ) {
				newlist.tools.push( this.tool.name );
				newlist.comment = 'Added tool to list';
			} else {
				const index = newlist.tools.indexOf( this.tool.name );
				newlist.tools.splice( index, 1 );
				newlist.comment = 'Removed tool from list';
			}
			this.$store.dispatch( 'lists/editList', newlist ).then(
				() => this.getMyLists() );
		}
	}
};
</script>

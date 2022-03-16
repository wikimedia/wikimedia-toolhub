<template>
	<v-row justify="center">
		<v-dialog
			v-model="itemEditComputed.itemDialogOpen"
			persistent
			max-width="600px"
		>
			<v-card>
				<v-form
					ref="itemform"
					v-model="valid"
					:disabled="!$can( 'add', 'toolinfo/tool' )"
				>
					<v-card-text>
						<v-container>
							<v-row>
								<v-col
									v-for="( uischema, id ) in uiSchema"
									:key="id"
									cols="12"
								>
									<InputWidget
										v-model="itemFields[ id ]"
										:schema="schema.properties[ id ]"
										:ui-schema="uischema"
									/>
								</v-col>
							</v-row>
						</v-container>
					</v-card-text>
					<v-card-actions>
						<v-spacer />
						<v-btn
							class="pa-4 mb-4"
							@click="cancel"
						>
							{{ $t( 'cancel' ) }}
						</v-btn>
						<v-btn
							color="primary base100--text"
							class="pa-4 mb-4"
							:disabled="!valid || !$can( 'add', 'toolinfo/tool' )"
							@click="addItem"
						>
							{{ $t( 'add' ) }}
						</v-btn>
					</v-card-actions>
				</v-form>
			</v-card>
		</v-dialog>
	</v-row>
</template>

<script>

import InputWidget from '@/components/common/InputWidget';

export default {
	name: 'ItemDialog',
	components: {
		InputWidget
	},
	props: {
		schema: {
			type: Object,
			default: () => {},
			required: true
		},
		uiSchema: {
			type: Object,
			default: () => {}
		},
		items: {
			type: [ Array ],
			default: null
		},
		itemEdit: {
			type: Object,
			default: () => {}
		}
	},
	data() {
		return {
			itemFields: { ...this.buildEmptyItemFields() },
			valid: false
		};
	},
	computed: {
		itemEditComputed() {
			return { ...this.itemEdit };
		}
	},
	methods: {
		addItem() {
			let replaced = false;
			const items = [ ...this.items ];
			items.some( ( _, index ) => {
				if ( index === this.itemEdit.index ) {
					items[ index ] = this.cleanItemFields();
					replaced = true;
					return replaced;
				}
				return false;
			} );

			if ( !replaced ) {
				items.push( this.cleanItemFields() );
			}

			this.$emit( 'update:items', items );
			this.cancel();
		},
		cancel() {
			this.itemFields = { ...this.buildEmptyItemFields() };

			this.$refs.itemform.reset();
			this.$emit( 'update:item-edit', {
				itemDialogOpen: false,
				item: null
			} );
		},
		/**
		 * Remove null fields.
		 *
		 * @return {Object}
		 */
		cleanItemFields() {
			return Object.keys( this.itemFields )
				.reduce( ( obj, key ) => {
					if ( this.itemFields[ key ] ) {
						obj[ key ] = this.itemFields[ key ];
					}
					return obj;
				}, {} );
		},
		buildEmptyItemFields() {
			const emptyItemFields = {};
			Object.keys( this.uiSchema ).forEach( ( key ) => {
				emptyItemFields[ key ] = null;
			} );
			return emptyItemFields;
		}
	},
	watch: {
		itemEdit: {
			handler( newVal ) {
				if ( newVal.item && !( newVal.item instanceof Event ) ) {
					this.itemFields = {
						...this.itemFields,
						...newVal.item
					};
				}
			},
			deep: true,
			immediate: true
		}
	}
};
</script>

<template>
	<v-row justify="center">
		<v-dialog
			v-model="authorEditComputed.authorDialogOpen"
			persistent
			max-width="600px"
		>
			<v-card>
				<v-form
					ref="authorform"
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
										v-model="authorFields[ id ]"
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
							@click="addAuthor"
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
	name: 'AuthorDialog',
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
		authors: {
			type: [ Array ],
			default: null
		},
		authorEdit: {
			type: Object,
			default: () => {}
		}
	},
	data() {
		return {
			authorFields: {
				name: null,
				wiki_username: null,
				developer_username: null,
				email: null,
				url: null
			},
			valid: false
		};
	},
	computed: {
		authorEditComputed() {
			return { ...this.authorEdit };
		}
	},
	methods: {
		addAuthor() {
			let replaced = false;
			const authors = [ ...this.authors ];

			authors.some( ( author, index ) => {
				if ( author.name === this.authorEdit.author?.name ) {
					authors[ index ] = this.cleanAuthorFields();
					replaced = true;
					return replaced;
				}
				return false;
			} );

			if ( !replaced ) {
				authors.push( this.cleanAuthorFields() );
			}

			this.$emit( 'update:authors', authors );
			this.cancel();
		},
		cancel() {
			this.authorFields = {
				name: null,
				wiki_username: null,
				developer_username: null,
				email: null,
				url: null
			};

			this.$refs.authorform.reset();
			this.$emit( 'update:author-edit', {
				authorDialogOpen: false,
				author: null
			} );
		},
		/**
		 * Remove null fields.
		 *
		 * @return {Object}
		 */
		cleanAuthorFields() {
			return Object.keys( this.authorFields )
				.reduce( ( obj, key ) => {
					if ( this.authorFields[ key ] ) {
						obj[ key ] = this.authorFields[ key ];
					}
					return obj;
				}, {} );
		}
	},
	watch: {
		authorEdit: {
			handler( newVal ) {
				if ( newVal.author ) {
					this.authorFields = { ...this.authorFields, ...newVal.author };
				}

			},
			deep: true,
			immediate: true
		}
	}
};
</script>

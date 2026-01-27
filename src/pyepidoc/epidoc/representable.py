from __future__ import annotations

from functools import cached_property, reduce
from pyepidoc.xml.xml_text import XmlText
from pyepidoc.xml.xml_element import (
    XmlComment, 
    XmlNode, 
    ProcessingInstruction
)

from pyepidoc.shared.namespaces import XMLNS
from pyepidoc.shared.enums import RegTextType
from .edition_element import EditionElement


class RepresentableElement(EditionElement):

    @property
    def elem_classes(self) -> dict[str, type[RepresentableElement]]:
        from .representable_classes import representable_classes
        return representable_classes

    @property
    def form_normalized(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>, <surplus> and <del> elements
        """
        return self.normalized_form
    
    @property
    def leiden_form(self) -> str:
        """
        Returns the form per Leiden conventions, i.e. with
        abbreviations expanded with brackets
        """
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_form`.')
        return self.representable_cls_inst.leiden_form

    @property
    def leiden_plus_form(self) -> str:
        """
        Returns the Leiden form, with 
        interpunts indicated by middle dot;
        line breaks are indicated with vertical bar '|'
        """

        def string_rep(n: XmlNode) -> str:
            """
            Get the string representation of the node, if it is 'g', 'lb', 'gap',
            otherwise return empty string.
            """
            ln = n.localname

            if isinstance(n, (XmlText, XmlComment, ProcessingInstruction)):
                return ''

            if ln in ['g', 'lb', 'gap']:
                return self.elem_classes[ln](n).leiden_form
            
            return ''

        def get_next_non_text(
                acc: list[XmlNode],
                node: XmlNode
            ) -> list[XmlNode]:

            if acc != []:
                last = acc[-1]

                if isinstance(last, XmlText):
                    if str(last).strip() not in ['', '·']:
                        return acc 
                
                if last.localname in ['lb', 'w', 'name', 'persName', 'roleName', 'num']:
                    return acc
            
            return acc + [node]

        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `leiden_plus_form`.')
        
        preceding = reversed(self.preceding_nodes_in_ab)
        following = self.following_nodes_in_ab

        preceding_upto_text = reduce(get_next_non_text, preceding, list[XmlNode]())
        preceding_upto_text = list(reversed(preceding_upto_text))
        following_upto_text = reduce(get_next_non_text, following, list[XmlNode]())
        
        prec_text = ''.join(map(string_rep, preceding_upto_text))
        following_text = ''.join(map(string_rep, following_upto_text))

        return prec_text + self.leiden_form + following_text        

    @cached_property
    def simple_lemmatized_edition_element(self) -> EditionElement:
        """
        Element for use in simple-lemmatized edition
        """
        t = type(self)
        elem = t(self.deepcopy()._e)
        elem._e.remove_children()
        elem._e.remove_attr('id', XMLNS)
        elem.text = self.simple_lemmatized_edition_form
        return elem
    
    @cached_property
    def simple_lemmatized_edition_form(self) -> str:
        """
        Form for use as text in the simple_lemmatized_edition_element
        """
        return self.normalized_form

    @cached_property
    def normalized_form(self) -> str:
        """
        Returns the normalized form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @orig_form
        """
        
        if self.representable_cls_inst is None:
            return self._e.text_desc
        if type(self.representable_cls_inst) is type(self):
            raise TypeError(f'Class {type(self)} must implement property `normalized_form`.')
        return self.representable_cls_inst.normalized_form
    
    @cached_property
    def orig_form(self) -> str:
        """
        Returns the original form of the token, i.e.
        taking the text from <reg> not <orig>, <corr> not <sic>;
        also excludes text from <g>.
        Compare @form and @normalized_form
        """
        non_ancestors = RegTextType.values()

        ancestors_str = ' and '.join([f'not(ancestor::ns:{ancestor})' 
                                 for ancestor in non_ancestors])

        normalized_text = self._e.xpath(f'descendant::text()[{ancestors_str}]')
        return self._e._clean_text(''.join([str(t) for t in normalized_text]))
    
    @property
    def representable_cls_inst(self) -> RepresentableElement | None:
        """
        An instance of a class inheriting from Representable giving 
        behaviours specific to the element in question, e.g. W, G, Expan etc.
        """

        cls = self.elem_classes.get(self._e.localname)
        if cls is None:
            return None
        inst = cls(self._e)
        return inst

    @property
    def type(self) -> str:
        return self._e.tag.name
